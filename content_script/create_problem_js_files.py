import re
import sys
import requests
import numpy as np
from urllib.parse import urlparse
import os
import shutil
import json

from create_dir import *
from create_content import *


fake_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def create_default_pathway(tutoring):
    return json.dumps(tutoring, indent=4)


def save_images(images, checksums, path, num, old_path):
    if type(images) != str:
        return "", num, ""
    
    images = images.split()
    names = []
    stored_checksums = checksums.split() if isinstance(checksums, str) and checksums else []
    updated_checksums = []

    for i in images:
        num += 1
        name = f"figure{num}.gif"
        names.append(name)

        i = re.sub(r"https://imgur\.com/([\d\w]+)", r"https://i.imgur.com/\g<1>.png", i)

        found = False
        for stored_md5 in stored_checksums:
            figures_dir = os.path.join(old_path, "figures")
            if os.path.isdir(figures_dir) and os.path.exists(os.path.join(figures_dir, name)) and \
                    create_image_md5(os.path.join(figures_dir, name)) == stored_md5:
                shutil.copyfile(os.path.join(figures_dir, name), os.path.join(path, name))
                updated_checksums.append(stored_md5)
                found = True
                break

        if found:
            continue

        try:
            r = requests.get(i, headers=fake_headers)
            r.raise_for_status()
        except (requests.exceptions.ConnectionError, ConnectionResetError):
            parse_result = urlparse(i)
            if parse_result.query:
                print(f"Image query params are not supported by the proxy. {i}")
                sys.exit(1)
            new_i = "https://cdn.statically.io/img/{}{}".format(parse_result.netloc, parse_result.path)
            print(f"Trying to proxy image {i} with {new_i}")
            try:
                r = requests.get(new_i, headers=fake_headers, timeout=10)
                r.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error saving image with proxy: {new_i}. Exception: {e}")
                continue
        except requests.exceptions.RequestException as e:
            print(f"Error saving image: {i}. Exception: {e}")
            continue

        with open(os.path.join(path, name), 'wb') as outfile:
            outfile.write(r.content)
        updated_checksums.append(create_image_md5(os.path.join(path, name)))

    return names, num, " ".join(updated_checksums)


def write_step_json(default_path, problem_name, row, step_count, tutoring, skills, images, figure_path,
                    default_pathway_json_path, path, verbosity, variabilization, latex, problem_skills, old_path):
    if step_count > 0:
        with open(default_pathway_json_path, "w", encoding="utf-8") as default_pathway:
            default_pathway.write(create_default_pathway(tutoring))

    tutoring = []
    step_count += 1
    current_step_name = f"{problem_name}{chr(96 + step_count)}"

    _, step_reg_json_path, default_pathway_json_path = create_step_dir(current_step_name, os.path.join(path, "steps"), verbosity)

    step_images, image_df_str = "", ""
    if isinstance(row.get("Images (space delimited)"), str):
        if not images:
            figure_path = create_fig_dir(path)
        step_images, images, image_df_str = save_images(row["Images (space delimited)"], row.get("Image Checksum", ""), 
                                                        figure_path, int(images), old_path)

    with open(step_reg_json_path, "w", encoding="utf-8") as step_file:
        if variabilization and type(row["Variabilization"]) != float:
            step_file.write(create_step(problem_name, row['Title'], row["Body Text"], row["Answer"], row["answerType"],
                                        step_count, row.get("mcChoices", ""), step_images, 
                                        var_str=row["Variabilization"], latex=latex, verbosity=verbosity))
        else:
            step_file.write(create_step(problem_name, row['Title'], row["Body Text"], row["Answer"], row["answerType"],
                                        step_count, row.get("mcChoices", ""), step_images, 
                                        latex=latex, verbosity=verbosity))

    skills[current_step_name] = problem_skills

    return step_count, current_step_name, tutoring, skills, images, figure_path, default_pathway_json_path, image_df_str


def write_subhint_json(row, row_type, current_step_name, current_subhints, oer, license, tutoring, previous_tutor, 
                       previous_images, images, path, figure_path, hint_dic, verbosity, variabilization, latex, old_path):
    hint_images, image_df_str = "", ""
    if isinstance(row.get("Images (space delimited)"), str):
        if not images:
            figure_path = create_fig_dir(path)
        hint_images, images, image_df_str = save_images(row["Images (space delimited)"], row.get("Image Checksum", ""), 
                                                        figure_path, int(images), old_path)

    hint_id = f"{row['Parent']}-{row['HintID']}"
    if row_type == 'hint':
        if variabilization and type(row["Variabilization"]) != float:
            subhint, subhint_id = create_hint(current_step_name, hint_id, row["Title"],
                                              row["Body Text"], oer, license, row["Dependency"], hint_images,
                                              hint_dic=hint_dic, var_str=row["Variabilization"],
                                              latex=latex, verbosity=verbosity)
        else:
            subhint, subhint_id = create_hint(current_step_name, hint_id, row["Title"],
                                              row["Body Text"], oer, license, row["Dependency"], hint_images,
                                              hint_dic=hint_dic, latex=latex, verbosity=verbosity)
    else:
        if variabilization and type(row["Variabilization"]) != float:
            subhint, subhint_id = create_scaffold(current_step_name, hint_id, row["Title"],
                                                  row["Body Text"], row["answerType"], row["Answer"],
                                                  row["mcChoices"], oer, license, row["Dependency"], hint_images,
                                                  hint_dic=hint_dic, var_str=row["Variabilization"],
                                                  latex=latex, verbosity=verbosity)
        else:
            subhint, subhint_id = create_scaffold(current_step_name, hint_id, row["Title"],
                                                  row["Body Text"], row["answerType"], row["Answer"],
                                                  row["mcChoices"], oer, license, row["Dependency"], hint_images,
                                                  hint_dic=hint_dic, latex=latex, verbosity=verbosity)

    hint_dic[row["HintID"]] = subhint_id
    current_subhints.append(subhint)
    tutoring.pop()

    if previous_tutor['Row Type'] == 'hint':
        if variabilization and type(previous_tutor["Variabilization"]) != float:
            previous, hint_id = create_hint(current_step_name, previous_tutor["HintID"],
                                            previous_tutor["Title"], previous_tutor["Body Text"], oer, license, 
                                            previous_tutor["Dependency"], previous_images,
                                            subhints=current_subhints, hint_dic=hint_dic,
                                            var_str=previous_tutor["Variabilization"],
                                            latex=latex, verbosity=verbosity)
        else:
            previous, hint_id = create_hint(current_step_name, previous_tutor["HintID"],
                                            previous_tutor["Title"], previous_tutor["Body Text"], oer, license, 
                                            previous_tutor["Dependency"], previous_images,
                                            subhints=current_subhints, hint_dic=hint_dic, latex=latex,
                                            verbosity=verbosity)
    else:
        if variabilization and type(previous_tutor["Variabilization"]) != float:
            previous, hint_id = create_scaffold(current_step_name, previous_tutor["HintID"],
                                                previous_tutor["Title"], previous_tutor["Body Text"],
                                                previous_tutor["answerType"], previous_tutor["Answer"],
                                                previous_tutor["mcChoices"], oer, license, 
                                                previous_tutor["Dependency"], previous_images,
                                                subhints=current_subhints, hint_dic=hint_dic,
                                                var_str=previous_tutor["Variabilization"],
                                                latex=latex, verbosity=verbosity)
        else:
            previous, hint_id = create_scaffold(current_step_name, previous_tutor["HintID"],
                                                previous_tutor["Title"], previous_tutor["Body Text"],
                                                previous_tutor["answerType"], previous_tutor["Answer"],
                                                previous_tutor["mcChoices"], oer, license, 
                                                previous_tutor["Dependency"], previous_images,
                                                subhints=current_subhints, hint_dic=hint_dic,
                                                latex=latex, verbosity=verbosity)
    tutoring.append(previous)

    return images, hint_dic, current_subhints, tutoring, figure_path, image_df_str


def write_hint_json(row, current_step_name, oer, license, tutoring, images, figure_path, path, hint_dic, verbosity, 
                    variabilization, latex, old_path):
    hint_images, image_df_str = "", ""
    if isinstance(row.get("Images (space delimited)"), str):
        if not images:
            figure_path = create_fig_dir(path)
        hint_images, images, image_df_str = save_images(row["Images (space delimited)"], row.get("Image Checksum", ""), 
                                                        figure_path, int(images), old_path)

    if variabilization and type(row["Variabilization"]) != float:
        hint, full_id = create_hint(current_step_name, row["HintID"], row["Title"],
                                    row["Body Text"], oer, license, row["Dependency"], hint_images,
                                    hint_dic=hint_dic, var_str=row["Variabilization"],
                                    latex=latex, verbosity=verbosity)
    else:
        hint, full_id = create_hint(current_step_name, row["HintID"], row["Title"],
                                    row["Body Text"], oer, license, row["Dependency"], hint_images,
                                    hint_dic=hint_dic, latex=latex, verbosity=verbosity)

    hint_dic[row["HintID"]] = full_id
    tutoring.append(hint)
    previous_tutor = row
    previous_images = hint_images

    return images, hint_dic, [], tutoring, previous_tutor, previous_images, figure_path, image_df_str


def write_scaffold_json(row, current_step_name, oer, license, tutoring, images, figure_path, path, hint_dic, verbosity, 
                        variabilization, latex, old_path):
    scaff_images, image_df_str = "", ""
    if isinstance(row.get("Images (space delimited)"), str):
        if not images:
            figure_path = create_fig_dir(path)
        scaff_images, images, image_df_str = save_images(row["Images (space delimited)"], row.get("Image Checksum", ""), 
                                                         figure_path, int(images), old_path)

    if variabilization and type(row["Variabilization"]) != float:
        scaff, full_id = create_scaffold(current_step_name, row["HintID"], row["Title"],
                                         row["Body Text"], row["answerType"], row["Answer"],
                                         row["mcChoices"], oer, license, row["Dependency"], scaff_images,
                                         hint_dic=hint_dic, var_str=row["Variabilization"],
                                         latex=latex, verbosity=verbosity)
    else:
        scaff, full_id = create_scaffold(current_step_name, row["HintID"], row["Title"],
                                         row["Body Text"], row["answerType"], row["Answer"],
                                         row["mcChoices"], oer, license, row["Dependency"], scaff_images,
                                         hint_dic=hint_dic, latex=latex, verbosity=verbosity)

    hint_dic[row["HintID"]] = full_id
    tutoring.append(scaff)
    previous_tutor = row
    previous_images = scaff_images

    return images, hint_dic, [], tutoring, previous_tutor, previous_images, figure_path, image_df_str


def write_problem_json(problem_row, problem_name, problem_json_path, course_name, sheet_name, images, path, 
                       figure_path, verbosity, variabilization, latex, old_path, lesson_id):
    problem_images, image_df_str = "", ""
    if isinstance(problem_row.get("Images (space delimited)"), str):
        if not images:
            figure_path = create_fig_dir(path)
        problem_images, images, image_df_str = save_images(problem_row["Images (space delimited)"], 
                                                           problem_row.get("Image Checksum", ""), 
                                                           figure_path, int(images), old_path)

    if variabilization and type(problem_row["Variabilization"]) != float:
        prob_js = create_problem_json(problem_name, problem_row["Title"], problem_row["Body Text"],
                                      problem_row["OER src"], problem_row["License"], problem_images,
                                      var_str=problem_row["Variabilization"], latex=latex,
                                      verbosity=verbosity, course_name=course_name, sheet_name=sheet_name, lesson_id=lesson_id)
    else:
        prob_js = create_problem_json(problem_name, problem_row["Title"], problem_row["Body Text"],
                                      problem_row["OER src"], problem_row["License"], problem_images, 
                                      latex=latex, verbosity=verbosity, course_name=course_name, 
                                      sheet_name=sheet_name, lesson_id=lesson_id)

    with open(problem_json_path, "w", encoding="utf-8") as file:
        file.write(prob_js)

    return figure_path, image_df_str
