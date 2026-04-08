import hashlib
import sys
import os
import pandas as pd
import time
import shutil
import gspread
from gspread_dataframe import set_with_dataframe
from openpyxl import load_workbook
import json
import re

from datetime import datetime, timezone
from process_sheet import process_sheet, get_all_url, get_sheet_online, get_sheet_values, get_sheet_with_retries, compute_sheet_hash, URL_SPREADSHEET_KEY


def normalize_values(values):
    """Pad rows to match header length, like get_all_values() does."""
    if not values:
        return values
    max_cols = max(len(row) for row in values) if values else 0
    return [row + [''] * (max_cols - len(row)) for row in values]


def sort_lessons(name):
    section = re.search(('[a-zA-Z\s]+([0-9]+)'), name)
    if section:
        section = int(section.group(1))
        subsection = re.search(('[a-zA-Z\s]+[0-9]+\.([0-9]+)'), name)
        if subsection:
            subsection = int(subsection.group(1))
        else:
            subsection = 50
    else:
        section = 100
        subsection = 50
    return section * 100 + subsection

def create_bkt_params(name):
    bkt_params = {
        name: {
            "probMastery": 0.1,
            "probTransit": 0.1,
            "probSlip": 0.1,
            "probGuess": 0.1
        }
    }

    return bkt_params


def create_lesson_plan(sheet, skills, lesson_id, meta):
    lesson_number = sheet.split()[0]
    lesson_topics = " ".join(sheet.split()[1:])

    lesson_name = ("Lesson " + lesson_number)

    lesson_plan = {
        "id": lesson_id,
        "name": lesson_name,
        "topics": lesson_topics,
        "allowRecycle": True,
        "learningObjectives": dict(zip(skills, [0.85 for _ in skills]))
    }

    if meta:
        lesson_plan.update(meta)

    return lesson_plan


def create_course_plan(course_name, lesson_plan, course_oer, course_license, editor=False, language="en"):
    if not lesson_plan:
        lesson_plan = []

    course_plan = {
        "courseName": course_name,
        "language": language,
        "courseOER": course_oer,
        "courseLicense": course_license,
        "lessons": lesson_plan
    }

    if editor:
        course_plan.update({
            "editor": True
        })

    return course_plan


def finish_course_plan(courses, file):
    file.write(json.dumps(courses, indent=4))
    file.close()


def finish_bkt_params(bkt_params, file):
    file.write(json.dumps(bkt_params, indent=4))
    file.close()

def finish_skill_model(bkt_params, file):
    file.write(json.dumps(bkt_params, indent=4))
    file.close()


def create_total(default_path, is_local, sheet_names=None, bank_url=None, full_update=False):
    """if sheet_names is not provided, default to run all sheets"""

    if is_local != "local" and is_local != "online":
        raise Exception("Running mode must be either 'local' or 'online")

    course_plan = old_course_plan = []
    bkt_params = old_bkt_params = {}
    skill_model: dict = {}

    skill_model_path = os.path.join("..", "skillModel.json")
    editor_content_path = os.path.join("..", "Editor Content")
    validator_path = os.path.join("..", ".OpenStax Validator")
    bkt_params_path = os.path.join("..", "bktParams.json")
    course_plans_path = os.path.join("..", "coursePlans.json")
    
    if full_update:
        if os.path.exists(skill_model_path):
            os.remove(skill_model_path)
        dest_path = os.path.dirname(default_path) + "/.OpenStax Content"
        if os.path.isdir(dest_path):
            shutil.rmtree(dest_path)
        os.makedirs(dest_path)
        if os.path.isdir(default_path):
            for file in os.listdir(default_path):
                shutil.move(os.path.join(default_path, file), dest_path)
            shutil.rmtree(default_path)
        if os.path.isdir(editor_content_path):
            shutil.rmtree(editor_content_path)
        if os.path.isdir(validator_path):
            shutil.rmtree(validator_path)

    else:
        if os.path.exists(skill_model_path):
            with open(skill_model_path) as skill_model_file:
                skill_model = json.load(skill_model_file)

        if os.path.exists(bkt_params_path):
            with open(bkt_params_path) as bkt_params_file:
                old_bkt_params = json.load(bkt_params_file)
            os.remove(bkt_params_path)

        if os.path.exists(course_plans_path):
            with open(course_plans_path) as course_plans_file:
                old_course_plan = json.load(course_plans_file)
            os.remove(course_plans_path)


    url_df, hash_df = get_all_url(bank_url=bank_url, is_local=is_local)
    hash_updates = []  # Track (sheet_name, spreadsheet_key, new_hash) for updating Content Hash tab

    sheets_queue = []
    for _, row in url_df.iterrows():

        # added language property
        course_name, course_language, book_url, book_oer, book_license, editor_url, editor_oer, editor_license = row['Book'], row["Language"], row['URL'], row['OER'], row['License'], row['Editor Sheet'], row['Editor OER'], row['Editor License']
        
        if type(book_url) == str and book_url:
            sheets_queue.append((book_url, False, course_name, book_oer, book_license, course_language))
        if type(editor_url) == str and editor_url:
            sheets_queue.append((editor_url, True, "", editor_oer, editor_license, "en"))
            
    for sheet_url, is_editor, course_name, course_oer, course_license, course_language in sheets_queue:
        lesson_plan = []
        if is_editor:
            course_name = "!!Editor Sheet " + hashlib.sha1(str(sheet_url).encode("utf-8")).hexdigest()[:6]

        if is_local == 'online':
            book = get_sheet_online(sheet_url)
            try:
                sheet_names = [sheet.title for sheet in book.worksheets() if sheet.title[:2] != '!!']
            except Exception as e:
                print("Gspread Error in {}, {}:".format(course_name, sheet_url), e)

        else:
            book = load_workbook(sheet_url)
            sheet_names = [sheet.title for sheet in book.worksheets if sheet.title[:2] != '!!']

        if full_update:
            mode = "full"
        else:
            mode = "final"

        # Book-level lastUpdateTime check to skip entirely unchanged books
        book_unchanged = False
        if is_local == 'online' and not full_update:
            try:
                last_update_time = book.get_lastUpdateTime()
                book_hash_rows = hash_df[hash_df["Spreadsheet Key"] == sheet_url]
                stored_times = book_hash_rows["Last Checked"]
                stored_times = stored_times[stored_times != '']
                if len(stored_times) > 0:
                    max_stored = str(stored_times.max())
                    if last_update_time <= max_stored:
                        book_unchanged = True
                        print("Book '{}' unchanged (lastUpdateTime: {}), skipping all worksheets".format(course_name, last_update_time))
            except Exception as e:
                print("Could not check lastUpdateTime for {}: {}".format(course_name, e))

        # Batch-read all worksheets for changed books to avoid sequential API calls
        batch_values = {}  # sheet_name -> normalized values
        if is_local == 'online' and not full_update and not book_unchanged:
            try:
                ranges = ["'{}'".format(s) for s in sheet_names]
                batch_result = book.values_batch_get(ranges)
                value_ranges = batch_result.get('valueRanges', [])
                for i, sheet in enumerate(sheet_names):
                    if i < len(value_ranges):
                        raw_values = value_ranges[i].get('values', [])
                        batch_values[sheet] = normalize_values(raw_values)
                    else:
                        batch_values[sheet] = []
            except Exception as e:
                print("Batch read failed for '{}': {}, falling back to sequential".format(course_name, e))
                batch_values = {}

        for sheet in sheet_names:
            # Determine whether this sheet needs processing
            if is_local == 'local' or full_update:
                should_process = True
            elif book_unchanged:
                should_process = False
            else:
                # Per-worksheet hash comparison using batch-fetched data
                should_process = False
                if sheet:
                    try:
                        if sheet in batch_values:
                            values = batch_values[sheet]
                        else:
                            ws = get_sheet_with_retries(book, sheet)
                            values = get_sheet_values(ws)
                        new_hash = compute_sheet_hash(values)
                        stored = hash_df[(hash_df["Sheet Name"] == sheet) & (hash_df["Spreadsheet Key"] == sheet_url)]
                        stored_hash = stored.iloc[0]["Content Hash"] if len(stored) > 0 else ""
                        if not stored_hash or stored_hash != new_hash:
                            should_process = True
                        hash_updates.append((sheet, sheet_url, new_hash))
                    except Exception as e:
                        print("Error checking hash for {}: {}".format(sheet, e))
                        should_process = True  # Process on error to be safe

            if should_process:
                start = time.time()
                # Prepare prefetched data if available from batch read
                prefetched_table = None
                prefetched_worksheet = None
                if sheet in batch_values and is_local == 'online':
                    prefetched_table = batch_values[sheet]
                    try:
                        prefetched_worksheet = get_sheet_with_retries(book, sheet)
                    except Exception as e:
                        print("Could not get worksheet object for {}: {}".format(sheet, e))

                if sheet[:2] == '##':
                    skills, lesson_id, skills_dict, meta = process_sheet(sheet_url, sheet, default_path, is_local, 'FALSE',
                                        course_name=course_name, mode=mode,
                                        prefetched_table=prefetched_table, prefetched_worksheet=prefetched_worksheet)
                    sheet = sheet[2:]
                else:
                    skills, lesson_id, skills_dict, meta = process_sheet(sheet_url, sheet, default_path, is_local, 'TRUE',
                                        course_name=course_name, mode=mode,
                                        prefetched_table=prefetched_table, prefetched_worksheet=prefetched_worksheet)
                if not lesson_id:
                    continue
                if not skills:
                    continue
                skill_model.update(skills_dict)
                skills.sort()
                lesson_plan.append(create_lesson_plan(sheet, skills, lesson_id, meta))
                for skill in skills:
                    bkt_params.update(create_bkt_params(skill))

                end = time.time()
                if is_local == "online" and end - start < 4.5:
                    time.sleep(4.5 - (end - start))
        
        if is_local == 'online' and not full_update:
            # Append everything from the old lesson_plan to the new lesson_plan
            old_lesson_plan = []
            for course in old_course_plan:
                if course["courseName"] == course_name:
                    old_lesson_plan = course["lessons"]
                    break

            new_lesson_ids = []
            for lesson in lesson_plan:
                new_lesson_ids.append(lesson["id"])

            for lesson in old_lesson_plan:
                if lesson["id"] not in new_lesson_ids:
                    lesson_plan.append(lesson)

        lesson_plan.sort(key=lambda lesson: sort_lessons(lesson["name"]))
        course_plan.append(create_course_plan(course_name, lesson_plan, course_oer, course_license, editor=is_editor, language=course_language))

    if is_local == 'online' and not full_update:
        # Append everything from the old bkt_params to the new bkt_params
        new_skills = list(bkt_params.keys())
        for skill, param in old_bkt_params.items():
            if skill not in new_skills:
                bkt_params.update({skill: param})

    file = open(os.path.join("..", "coursePlans.json"), "w")
    finish_course_plan(course_plan, file)

    file = open(os.path.join("..", "bktParams.json"), "w")
    finish_bkt_params(bkt_params, file)

    file = open(os.path.join("..", "skillModel.json"), "w")
    finish_skill_model(skill_model, file)

    # Update Content Hash tab with new hashes and timestamps
    if is_local == "online" and hash_updates:
        now = datetime.now(timezone.utc).isoformat()
        for sheet_name, spreadsheet_key, content_hash in hash_updates:
            mask = (hash_df["Sheet Name"] == sheet_name) & (hash_df["Spreadsheet Key"] == spreadsheet_key)
            if mask.any():
                hash_df.loc[mask, "Content Hash"] = content_hash
                hash_df.loc[mask, "Last Checked"] = now
            else:
                new_row = pd.DataFrame([{
                    "Sheet Name": sheet_name,
                    "Content Hash": content_hash,
                    "Spreadsheet Key": spreadsheet_key,
                    "Last Checked": now
                }])
                hash_df = pd.concat([hash_df, new_row], ignore_index=True)

        try:
            bank_book = get_sheet_online(URL_SPREADSHEET_KEY)
            try:
                hash_sheet = bank_book.worksheet('!!Content Hash')
            except gspread.exceptions.WorksheetNotFound:
                hash_sheet = bank_book.add_worksheet(title='!!Content Hash', rows=1000, cols=4)
            hash_sheet.clear()
            set_with_dataframe(hash_sheet, hash_df)
        except Exception as e:
            print('Failed to update !!Content Hash tab: {}'.format(e))
    
    if full_update and os.path.isdir(dest_path):
        shutil.rmtree(dest_path)

if __name__ == '__main__':
    is_local = sys.argv[1]
    sheet_names = sys.argv[2:]
    create_total('../OpenStax Content', is_local, sheet_names)
