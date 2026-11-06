"""
generate_alt_text.py

Fills in the "Alt Text (pipe delimited)" column of the OATutor content
spreadsheet using OpenAI's vision-capable models, for rows that:
  1. Have at least one image URL in "Images (space delimited)", AND
  2. Do NOT already have alt text in "Alt Text (pipe delimited)"
     (never overwrites existing content-team entries, except via
     --refresh-key, see below).

Works directly off an exported CSV of the sheet -- no local clone of
OATutor-Content needed, since the Images column holds live, publicly
hosted URLs (e.g. postimg.cc) that OpenAI's API can fetch on its own.

FEATURES
--------
- Concurrent processing: multiple images described in parallel.
- Checkpointing: every completed row is saved to a JSON file next to your
  CSV as soon as it finishes.
- Resume: rerun the same command after a crash/Ctrl-C/rate limit and
  already-completed rows are skipped, not redone.
- Retries with exponential backoff for transient API/network failures.
- --force-refresh: ignore the checkpoint cache and regenerate alt text
  for every row that's still blank in the sheet (does NOT touch rows
  that already have manually-written alt text).
- --refresh-key <hash>: regenerate one specific row, identified by its
  row_key hash (printed in the script's own output/checkpoint file),
  even if it already has alt text -- for spot-fixing a bad description
  without redoing the whole run. Repeatable: --refresh-key a1b2... --refresh-key c3d4...
- --push-to-sheet: after writing the CSV, also push the newly-filled
  values directly into the live Google Sheet via a service account,
  with a safety check that aborts per-row (not the whole run) if the
  local and live rows don't match, so a reordered sheet can't silently
  get the wrong alt text written into the wrong row.

SETUP
-----
See scripts/README.md. In short, from scripts/: pip install -r requirements.txt,
put OPENAI_API_KEY in scripts/.env, and the service account file at
scripts/credentials/service-account-credentials.json (only needed for sheet access).

    python generate_alt_text.py rows.csv --domain algebra --model gpt-5.5

Useful flags:
    --domain data-science|algebra  course-specific part of the prompt (default data-science)
    --model <name>              OpenAI vision model (default gpt-4o; gpt-5.5 read graphs better)
    --workers 8                 images described in parallel (default 6)
    --limit 20                  only process the first N rows needing alt text
    --force-refresh              regenerate blank rows even if cached
    --refresh-key <hash>         regenerate one specific row (repeatable)
    --push-to-sheet               also write results into the live sheet
    --spreadsheet-id <id>         required with --push-to-sheet
    --worksheet-name <name>       required with --push-to-sheet
    --service-account <path>      default: credentials/service-account-credentials.json

OUTPUT
------
    <input>_with_alt_text.csv          -- the sheet, ready to paste back
    <input>_alt_text_checkpoint.json   -- resume file, safe to delete once
                                           you're done and have pasted (or
                                           pushed) the results
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads .env in the current directory into the environment,
                # so OPENAI_API_KEY doesn't need to be exported manually

# ---- Column names: edit if your sheet's headers differ --------------------
IMAGES_COL = "Images (space delimited)"
ALT_TEXT_COL = "Alt Text (pipe delimited)"
TITLE_COL = "Title"
BODY_COL = "Body Text"
PROBLEM_NAME_COL = "Problem Name"
ROW_TYPE_COL = "Row Type"
HINT_ID_COL = "HintID"

MULTI_IMAGE_JOINER = " | "
MODEL = "gpt-4o"  # set from --model in main()
MAX_TOKENS = 600  # 300 cut some long table descriptions off mid-sentence
REASONING_MAX_TOKENS = 4000  # reasoning models count their hidden reasoning against the limit too
REASONING_MODEL_PREFIXES = ("gpt-5", "o1", "o3", "o4")
DEFAULT_WORKERS = 6
MAX_RETRIES = 3
CHECKPOINT_DIR = Path("data/checkpoints")

CORE_PROMPT = """You write alt text for images embedded in math, \
statistics, and data science tutoring problems (OATutor, an adaptive \
tutoring platform). Follow WCAG 1.1.1 guidance:
- Describe the informational content of the image, not its appearance.
- Do not start with "Image of" or "Picture of".
- Always include every number, label, or value shown in the image that a \
sighted student would read directly off it -- even if that same \
information is later revealed piecemeal through hints or scaffolded \
steps elsewhere in the problem. The alt text must stand completely on \
its own.
- Do not add teaching commentary or hints toward the answer -- describe \
only what is shown.
- Never state anything the student is being asked to work out from the \
image -- for example the domain or range of a graph, the solution of an \
inequality, or the set a number line shows -- unless that exact text is \
printed in the image. Describe the marks and labels; the student draws \
the conclusion.
- If the image includes an actual question or directive telling the \
student what to do (e.g. starts with "(b) Write a line of code...", or \
a lettered/numbered sub-part), read that text verbatim, before \
describing any table or code that follows it. Do not prefix it with a \
label like "INSTRUCTIONS:" -- just include the text itself.
- Bullet points that DESCRIBE or DEFINE something -- function argument \
descriptions (e.g. "tbl (Table): a table with the data points used to \
generate the regression line"), or text explaining what a table's \
columns mean -- are NOT the directive and should be paraphrased, not \
read verbatim. Never repeat this kind of descriptive text a second time \
anywhere else in the output.
- If an image opens with narrative or scenario-setting prose (a story, \
a hypothesis, a setup like "a friend gives you a table called X") \
rather than a direct question, that text is not a directive either -- \
but never skip it silently. Paraphrase it, usually together with any \
column-defining bullets that follow it (see DATA TABLES below, when \
present, for the exact pattern).
- Never output a literal "\\n" or other escape sequence -- use normal \
spacing and punctuation instead.
- Never use markdown formatting -- no backticks around code/variable \
names, no dashes or asterisks as bullets, no bold/italic markers. This \
is read aloud by screen readers as plain text; formatting characters \
would be read aloud too (e.g. a screen reader says "backtick" for each \
`). Write everything as plain prose.
- To summarize what's verbatim vs. paraphrased: the directive/question \
itself and a table's actual row data (real values) are transcribed \
verbatim, since that's information a student needs exactly as shown. \
Descriptive/definitional bullet text (argument descriptions, column \
explanations) and all code are paraphrased -- see the course-specific \
sections below, when present, for how.
- Output ONLY the alt text itself, nothing else (no quotes, no preamble).

MATH EQUATIONS:
- Verbalize math notation into words a screen reader can read smoothly \
-- do not reproduce raw Unicode math symbols (like hats, subscripts, \
superscripts, or special characters) as-is. Screen readers handle these \
unreliably, often skipping or mispronouncing them.
- Spell out: hats as "hat" (theta-hat), subscripts as "sub" (x sub i), \
superscripts as "squared"/"cubed"/"to the power of n", Greek letters by \
name (theta, lambda, sigma), and operators in words (times, divided by, \
plus or minus).
WRONG: "self_rating = θ̂₀ + θ̂₁ × critic_1"
RIGHT: "self_rating equals theta-hat sub 0 plus theta-hat sub 1 times \
critic_1"
"""

# Course-type guidance, chosen with --domain and appended to CORE_PROMPT.
# Data 8 and Data 100 used CORE_PROMPT + DATA_SCIENCE_PROMPT (Natalie's original prompt).
DATA_SCIENCE_PROMPT = """DATA TABLES:
- State a column's unit (%, $, etc.) once, as part of naming that column \
-- do not repeat the unit on every row's value.
- List rows in the form "Row 1: value, value, value; Row 2: value, value, \
value; ..." -- a semicolon between rows, commas between values within a \
row, numbered starting at 1.
- Do not wrap text values in quotation marks.
- If a column is blank / left for the student to fill in (e.g. a "Bar \
Height" answer column), say so once when naming the columns, rather than \
repeating "(blank)" on every row.
- Some images open with narrative or scenario-setting prose before the \
table -- a story, a hypothesis, a "friend gives you a table called X" \
setup -- rather than a direct question. This is NOT a directive (don't \
read it verbatim, don't label it INSTRUCTIONS), but it must NEVER be \
skipped either, since it's what tells the reader what the table \
represents. Paraphrase this narrative TOGETHER WITH any column-defining \
bullet points into one or two flowing summary sentences, then follow \
with the exact table contents.
Example: an image opens with a paragraph about students claiming crowd \
noise affects an opposing team's score, followed by bullet points \
defining an Opponent/Loudness/Points table, followed by 2024-season row \
data. Paraphrase as: "The image shows a description and a table related \
to a hypothesis about noise levels and opponents' scores at Cal football \
games. The table is titled noise and contains three columns: Opponent, \
Loudness, and Points. Opponent is Cal's opponent for the game. Loudness \
is the maximum noise in decibels produced by the student section. Points \
is the number of points scored by the opposing team. The table includes \
data from the 2024 season: Row 1: UC Davis, 65, 13; Row 2: Auburn, 55, \
14; ..." -- then the remaining rows verbatim.
- If the image includes written text explaining what the table's columns \
mean (e.g. "item (string): name of the pastry"), paraphrase that \
explanatory text INSTEAD of separately naming the columns yourself and \
INSTEAD of reading it verbatim -- do not state the column names twice. \
Follow it with the raw table contents (exact values, not paraphrased).
- If there's no such explanatory text, open with a brief "Table with \
columns X, Y, Z." before the row contents.
Example, for a table with columns Dollars, Students (%), and a blank Bar \
Height column, no explanatory text present, and rows 500-800/15, \
800-1000/25, 1000-1200/40, 1200-1600/20:
"Table with columns Dollars, Students (%), and Bar Height (blank, for \
the student to fill in). Row 1: 500-800, 15; Row 2: 800-1000, 25; Row 3: \
1000-1200, 40; Row 4: 1200-1600, 20."

WRONG -- do not do this (reads the column explanations verbatim instead \
of paraphrasing, AND states the column names twice):
"Table with columns item, category, price, and satisfaction. The table \
has 4 columns: item (string): name of the pastry; category (string): \
whether the pastry is sweet or savory; ... Row 1: ..."
RIGHT for a table WITH explanatory text present (paraphrased once, row \
data exact):
"A table of pastries with their category, price, and a satisfaction \
rating out of 10. Row 1: Hot Dog Bun, Savory, 2.75, 8.5; Row 2: Yudane \
Milk Bun, Sweet, 2.99, 9; ..."

CODE -- FULLY WRITTEN (no blanks):
- Reminder: if a lettered/numbered question or directive appears above \
this code (e.g. "(b) Write a function that..."), include that text \
verbatim, as its own sentence, before describing the code -- do not skip \
straight to the code description.
- Introduce it as a finished, complete function -- name the function and \
its arguments -- then paraphrase what it does, rather than replaying \
every line verbatim.
Example: "A function defined as square, with one argument, a. It \
multiplies a by itself and returns the result."

CODE -- SKELETON / FILL-IN-THE-BLANK:
- Reminder: if a lettered/numbered question or directive appears above \
this code (e.g. "(b) Write a function that..."), include that text \
verbatim, as its own sentence, before describing the code -- do not skip \
straight to the code description.
- Introduce it as a fill-in-the-blank / skeleton code block. If it's a \
function definition, name the function.
Example opening: "A fill-in-the-blank code block defining the function \
bootstrap."
- Then paraphrase, a bit more descriptively than a bare list: note what \
variables are defined and what blanks exist, so a student understands \
the shape of what they need to fill in -- without ever using literal \
underscores ("____") to represent a blank. Describe blanks in words \
("a blank," "two blanks") instead.
Example, full: "A fill-in-the-blank code block defining the function \
top_n, with three arguments: tbl, col, and n. Inside, sorted_tbl is set \
to a blank, top_n_rows is set to a blank, and the function returns a \
blank."

WRONG -- do not do this (transcribes the literal blank/underscore \
markers instead of describing the code):
"def fitted_value(tbl, x, y, x0): m = ________________________________ \
b = ________________________________ ________________________________"
RIGHT:
"Defines the function fitted_value with arguments tbl, x, y, and x0. \
Inside the function: m is assigned a blank, b is assigned a blank, \
followed by a blank line."

SCATTER PLOTS / GRAPHS WITH MULTIPLE DATA POINTS:
- Do NOT state exact coordinates for individual points -- this applies \
NO MATTER HOW FEW points are in the plot. It is tempting to list exact \
coordinates when there are only 3-8 points, since it feels precise and \
manageable, but reading positions off a plot is unreliable at any \
count -- a wrong coordinate stated confidently is worse than a \
qualitative description, even for a plot with just a few points.
- Instead, describe: the axis labels and ranges, roughly which region \
of the plot each group/color/marker occupies, how spread out or tightly \
clustered each group is, and any clear relationship between groups \
(overlapping, separated, one group consistently higher than another).
- If multiple similar plots are shown side by side (e.g. several \
labeled "Clustering A/B/C"), describe what's the same and what \
meaningfully differs between them, rather than re-describing each one \
from scratch in full detail.
Example: "Three scatter plots labeled Clustering A, Clustering B, and \
Clustering C, each with three groups of points shown as orange circles, \
blue crosses, and green stars. In all three plots, the orange circles \
sit in the lower-left region, the blue crosses are scattered in the \
upper-middle area, and the green stars are in the lower-right region. \
The three plots are similar overall, with only minor differences in \
exactly how spread out each group is."
WRONG even with few points: "Class A points are located at (-2, 1), \
(-1, 2), (0, 3), (1, 2), and (2, 1)."
RIGHT: "Class A points form a rough arc across the middle of the plot, \
peaking near the center; Class B points cluster just below and to the \
left of that arc."
"""

# Algebra / precalculus figures (OpenStax-style): number lines, counters, function graphs.
ALGEBRA_PROMPT = """NUMBER LINES:
- Name the range of tick labels shown (e.g. "A number line from -5 to \
5").
- Say exactly which part is shaded or drawn: which direction it runs, \
where it starts and stops, and whether it continues forever (an arrow \
at the end).
- For every endpoint, say whether it is included or excluded, and name \
the mark that shows it: a bracket or filled dot means included, a \
parenthesis or open dot means excluded. Never leave this out -- it is \
often the whole point of the image.
- Read any inequality or interval notation printed on the image, in \
words: "x is less than or equal to 1", "the interval from negative \
infinity to 1, including 1". Do not use symbols like ≤, ∞, or ∪.
- Read fractions and mixed numbers as words ("nine eighths", "negative \
three fifths"). If a label is too small or unclear to read with \
certainty, say it is unclear rather than guessing a value.
- Labels often sit right next to each other, such as a tick label 2 \
beside a fraction label at a bracket just past it. Treat them as \
separate labels on separate marks; do not merge them into one mixed \
number.
Example: "A number line from -4 to 6, labeled x is greater than or equal \
to -2. It is shaded from -2 to the right, with an arrow showing it \
continues forever. A bracket at -2 shows that -2 is included. Below it, \
the interval from -2 to infinity, including -2."

COUNTERS AND OTHER MANIPULATIVES:
- Count every object and give its color. In these materials, blue \
counters stand for positive ones and red counters stand for negative \
ones -- say so, so color is not the only way the meaning comes across.
- Describe any grouping, such as a circled pair of one positive and one \
negative counter (a pair that cancels to zero).
- Read any expression or result printed next to the counters.
Example: "Three red counters, each representing negative one, labeled \
negative 1 plus negative 2, with the result negative 3."

GRAPHS OF FUNCTIONS ON A GRID:
- Give the axis labels and the range of values shown on each axis.
- Describe the shape of the curve from left to right (rises, falls, \
turning points).
- State the coordinates of key points that sit exactly on grid lines: \
endpoints, turning points, and intercepts. For every endpoint, say \
whether it is an open dot (excluded) or a filled dot (included), or \
whether the curve continues with an arrow.
- Do not estimate coordinates for points between grid lines.

CHARTS OF REAL-WORLD DATA:
- Give the title, what each axis measures with its units, and the range \
of each axis with its tick spacing ("0 to 2,200 in steps of 200"). Do \
not list every tick label.
- Describe the overall trend over time and where the highest and lowest \
values occur, using approximate values ("about 2,000 thousand barrels \
per day around 1988").
"""

DOMAIN_PROMPTS = {
    "data-science": DATA_SCIENCE_PROMPT,
    "algebra": ALGEBRA_PROMPT,
}

# Set from --domain in main(); defaults to the prompt Data 8 and Data 100 were generated with.
SYSTEM_PROMPT = CORE_PROMPT + "\n" + DATA_SCIENCE_PROMPT

# One description per image URL per run, so an image reused across many hints
# gets the same alt text everywhere (and is only paid for once).
_url_cache: dict[str, str] = {}
_url_locks: dict[str, threading.Lock] = {}
_url_locks_guard = threading.Lock()


def describe_image_cached(client: OpenAI, url: str, context: str) -> str | None:
    """Describes each URL once; workers that hit the same URL wait for the first one's result."""
    with _url_locks_guard:
        lock = _url_locks.setdefault(url, threading.Lock())
    with lock:
        if url not in _url_cache:
            alt = describe_image_with_retry(client, url, context)
            if not alt:
                return None
            _url_cache[url] = alt
        return _url_cache[url]


def normalize_image_url(url: str) -> str | None:
    """Best-effort cleanup for known non-direct-link hosts."""
    url = url.strip()
    if not url:
        return None
    if "drive.google.com" in url and "/view" in url:
        try:
            file_id = url.split("/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        except IndexError:
            print(f"[warn] couldn't parse Drive file id out of: {url}")
            return url
    return url


def row_key(row) -> str:
    """
    Stable identifier for a row, independent of its position in the CSV.
    Hashing on content (not row number) means the checkpoint still matches
    correctly even if rows get added/reordered in the sheet between runs.
    Printed alongside every result -- copy one into --refresh-key to
    regenerate just that row later.
    """
    raw = "|".join([
        row.get(PROBLEM_NAME_COL, ""),
        row.get(ROW_TYPE_COL, ""),
        row.get(HINT_ID_COL, ""),
        row.get(IMAGES_COL, ""),
    ])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


class Checkpoint:
    """Thread-safe, flush-on-every-write JSON checkpoint file."""

    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self.data = {}
        if path.exists():
            self.data = json.loads(path.read_text())
            print(f"Loaded checkpoint with {len(self.data)} previously completed rows from {path}")

    def get(self, key: str):
        return self.data.get(key)

    def set(self, key: str, value: str):
        with self.lock:
            self.data[key] = value
            self.path.write_text(json.dumps(self.data, indent=2))


def clean_alt_text(text: str) -> str:
    """
    Deterministic cleanup applied to every model response, independent of
    whether the prompt's formatting instructions were followed. Currently:
    - collapses literal "\\n"/"\\t" escape sequences and real
      newlines/tabs into single spaces, since the model doesn't reliably
      avoid these on its own even when explicitly told not to.
    - strips a single pair of matching quote marks wrapping the ENTIRE
      response (e.g. the model sometimes returns '"actual text"' despite
      being told not to quote its output). Only strips when the first
      and last character are a matching quote AND removing them still
      leaves a sane, non-trivial string -- this avoids mangling a
      legitimate case where the alt text itself is meant to describe a
      quoted string literal shown in code.
    """
    text = text.replace("\\n", " ").replace("\\t", " ")
    text = re.sub(r"\s*[\n\t]\s*", " ", text)
    text = re.sub(r" {2,}", " ", text).strip()

    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        inner = text[1:-1].strip()
        # Only unwrap if the inside doesn't itself start/end with the
        # same quote char again (which would suggest genuinely nested
        # quoting we shouldn't touch) and isn't empty.
        if inner and not (inner[0] == text[0] or inner[-1] == text[0]):
            text = inner
    return text


def describe_image(client: OpenAI, image_url: str, context: str) -> str:
    head = requests.head(image_url, timeout=10, allow_redirects=True)
    if head.status_code >= 400:
        raise RuntimeError(f"HTTP {head.status_code} fetching {image_url}")

    response = client.chat.completions.create(
        model=MODEL,
        **completion_params(MODEL),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Problem/hint context (for reference only, don't "
                            f"restate it verbatim): {context}\n\n"
                            "Write alt text for this image."
                        ),
                    },
                    # "auto" can pick low resolution for small figures, which misread grid coordinates
                    {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}},
                ],
            },
        ],
    )
    choice = response.choices[0]
    if choice.finish_reason == "length":
        print(f"[fail] {image_url}: description hit the token limit and was cut off, not saving it")
        return None
    return clean_alt_text(choice.message.content)


def completion_params(model: str) -> dict:
    """Reasoning models (GPT-5, o-series) reject temperature and need room for hidden reasoning tokens."""
    if model.startswith(REASONING_MODEL_PREFIXES):
        return {"max_completion_tokens": REASONING_MAX_TOKENS}
    return {"max_completion_tokens": MAX_TOKENS, "temperature": 0}


def describe_image_with_retry(client: OpenAI, url: str, context: str) -> str | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return describe_image(client, url, context)
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"[fail] giving up on {url} after {MAX_RETRIES} attempts: {e}")
                return None
            wait = 2 ** attempt
            print(f"[retry {attempt}/{MAX_RETRIES}] {url} failed ({e}), retrying in {wait}s")
            time.sleep(wait)


def process_row(client: OpenAI, checkpoint: Checkpoint, key: str, images_raw: str,
                 context: str, force: bool):
    """Runs in a worker thread. Unless `force` is set, checks the
    checkpoint first (resume path). Otherwise calls the API for each
    image URL in this row and saves the combined result before returning."""
    if not force:
        cached = checkpoint.get(key)
        if cached is not None:
            return cached, True  # (result, was_resumed)

    urls = [u for u in images_raw.split() if u.strip()]
    descriptions = []
    for url in urls:
        clean_url = normalize_image_url(url)
        alt = clean_url and describe_image_cached(client, clean_url, context)
        if not alt:
            # the tooling pairs the Nth alt text with the Nth image, so a row with a gap would
            # describe the wrong images; leave the whole row blank for the next run instead
            print(f"[skip] no description for {url}, leaving this row's alt text blank")
            return None, False
        descriptions.append(alt)

    result = MULTI_IMAGE_JOINER.join(descriptions) if descriptions else None
    if result:
        checkpoint.set(key, result)
    return result, False


def push_to_sheet(df: pd.DataFrame, touched_indices: list[int], args):
    """Writes newly-filled alt text directly into the live Google Sheet.

    Safety: before writing any given row, it compares Problem Name and Row
    Type between the local dataframe and the live sheet at that row number.
    If they don't match -- meaning the sheet has been reordered/edited
    since this CSV was exported -- that single row is skipped with a
    warning instead of writing alt text into the wrong place. One bad
    match doesn't abort the rest of the push.
    """
    try:
        import gspread
    except ImportError:
        print("[error] --push-to-sheet requires gspread. Run: pip install gspread --break-system-packages")
        return

    if not args.spreadsheet_id or not args.worksheet_name:
        print("[error] --push-to-sheet requires --spreadsheet-id and --worksheet-name")
        return

    gc = gspread.service_account(filename=args.service_account)
    sh = gc.open_by_key(args.spreadsheet_id)
    ws = sh.worksheet(args.worksheet_name)

    sheet_values = ws.get_all_values()
    if not sheet_values:
        print("[error] live worksheet appears empty")
        return
    header = sheet_values[0]

    if ALT_TEXT_COL not in header:
        print(f"[error] '{ALT_TEXT_COL}' isn't a column in '{args.worksheet_name}' yet -- "
              f"add that header in the sheet first, then rerun with --push-to-sheet.")
        return

    col_num = header.index(ALT_TEXT_COL) + 1
    name_col_idx = header.index(PROBLEM_NAME_COL) if PROBLEM_NAME_COL in header else None
    type_col_idx = header.index(ROW_TYPE_COL) if ROW_TYPE_COL in header else None

    updates = []
    skipped_mismatch = 0

    for idx in touched_indices:
        sheet_row_num = idx + 2  # row 1 is the header, df is 0-indexed
        if sheet_row_num - 1 >= len(sheet_values):
            print(f"[warn] row {idx}: would map past the end of the live sheet ({len(sheet_values)} rows), skipping")
            skipped_mismatch += 1
            continue

        live_row = sheet_values[sheet_row_num - 1]

        if name_col_idx is not None and live_row[name_col_idx] != df.at[idx, PROBLEM_NAME_COL]:
            print(
                f"[warn] row {idx}: local vs. live mismatch on {PROBLEM_NAME_COL} "
                f"('{df.at[idx, PROBLEM_NAME_COL]}' vs '{live_row[name_col_idx]}') -- "
                f"skipping this row rather than risk writing to the wrong place"
            )
            skipped_mismatch += 1
            continue

        if type_col_idx is not None and live_row[type_col_idx] != df.at[idx, ROW_TYPE_COL]:
            print(
                f"[warn] row {idx}: local vs. live mismatch on {ROW_TYPE_COL} -- skipping this row"
            )
            skipped_mismatch += 1
            continue

        updates.append({
            "range": gspread.utils.rowcol_to_a1(sheet_row_num, col_num),
            "values": [[df.at[idx, ALT_TEXT_COL]]],
        })

    if updates:
        ws.batch_update(updates)  # one batched API call, not one per row

    print(
        f"Pushed {len(updates)} alt text values directly to '{args.worksheet_name}'"
        + (f", skipped {skipped_mismatch} due to identity mismatch (check these manually)" if skipped_mismatch else "")
        + "."
    )


def build_work_items(df: pd.DataFrame, refresh_keys: set[str], force_refresh: bool):
    """
    Shared between CSV mode and sheet mode: decides which rows need
    processing, and whether each one bypasses the checkpoint/existing-alt
    check (force_refresh or a targeted --refresh-key match).
    Returns (work_items, skipped_has_alt, skipped_no_image, unmatched_refresh_keys).
    """
    work_items = []  # (row_index, key, images_raw, context, force_this_row)
    skipped_has_alt = skipped_no_image = 0
    matched_refresh_keys = set()

    for idx, row in df.iterrows():
        images_raw = row.get(IMAGES_COL, "").strip()
        existing_alt = row.get(ALT_TEXT_COL, "").strip()
        key = row_key(row)
        is_targeted_refresh = key in refresh_keys
        if is_targeted_refresh:
            matched_refresh_keys.add(key)

        if not images_raw:
            skipped_no_image += 1
            continue

        if existing_alt and not is_targeted_refresh:
            skipped_has_alt += 1
            continue

        force_this_row = force_refresh or is_targeted_refresh
        context = f"{row.get(TITLE_COL, '')} {row.get(BODY_COL, '')}".strip()
        work_items.append((idx, key, images_raw, context, force_this_row))

    unmatched = refresh_keys - matched_refresh_keys
    return work_items, skipped_has_alt, skipped_no_image, unmatched


def run_work_items(client: OpenAI, checkpoint: Checkpoint, work_items, workers: int):
    """Shared execution loop: runs process_row across a thread pool and
    returns (df_updates, filled_count, resumed_count) where df_updates is
    a dict of {row_index: alt_text} for every row that got a result."""
    filled = resumed = 0
    updates = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(process_row, client, checkpoint, key, images_raw, context, force): idx
            for idx, key, images_raw, context, force in work_items
        }
        for future in as_completed(futures):
            idx = futures[future]
            result, was_resumed = future.result()
            if result:
                updates[idx] = result
                filled += 1
                resumed += was_resumed
                tag = "resumed" if was_resumed else "ok"
                print(f"[{tag}] row {idx + 2}: {result[:90]}")
    return updates, filled, resumed


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", name).strip("_")


def extract_spreadsheet_id(url: str) -> str:
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        raise ValueError(f"Couldn't find a spreadsheet ID in URL: {url}")
    return match.group(1)


def process_tab(client: OpenAI, ws, spreadsheet_id: str, args) -> None:
    """Reads one worksheet directly from Google Sheets, generates alt text
    for rows that need it, and either writes results straight back to that
    same worksheet (default) or just prints what it would have written
    (--dry-run). Uses its own checkpoint file, separate from every other
    tab, so pausing partway through one tab never affects another."""
    print(f"\n=== Tab: {ws.title} ===")
    values = ws.get_all_values()
    if not values:
        print(f"[skip] '{ws.title}' is empty")
        return

    header = values[0]
    if IMAGES_COL not in header:
        print(f"[skip] '{ws.title}' has no '{IMAGES_COL}' column -- doesn't look like content data, skipping")
        return
    if ALT_TEXT_COL not in header:
        print(f"[skip] '{ws.title}' has no '{ALT_TEXT_COL}' column yet -- "
              f"add that header in the live sheet first, then rerun")
        return

    df = pd.DataFrame(values[1:], columns=header).fillna("")
    df[PROBLEM_NAME_COL] = df[PROBLEM_NAME_COL].replace("", pd.NA).ffill().fillna("")

    checkpoint_path = CHECKPOINT_DIR / f"{sanitize_filename(spreadsheet_id[:8])}_{sanitize_filename(ws.title)}_checkpoint.json"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = Checkpoint(checkpoint_path)

    refresh_keys = set(args.refresh_key)
    work_items, skipped_has_alt, skipped_no_image, unmatched = build_work_items(
        df, refresh_keys, args.force_refresh
    )
    for k in unmatched:
        print(f"[warn] --refresh-key {k} didn't match any row in '{ws.title}'")

    if args.limit:
        work_items = work_items[: args.limit]

    if not work_items:
        print(f"Nothing to do in '{ws.title}' ({skipped_has_alt} already had alt text, {skipped_no_image} had no images).")
        return

    print(
        f"{len(work_items)} rows to process in '{ws.title}' "
        f"({skipped_has_alt} already had alt text, {skipped_no_image} had no images)."
    )

    updates, filled, resumed = run_work_items(client, checkpoint, work_items, args.workers)

    if not updates:
        print(f"No results generated for '{ws.title}'.")
        return

    col_num = header.index(ALT_TEXT_COL) + 1
    if args.dry_run:
        for idx, alt_text in updates.items():
            sheet_row_num = idx + 2
            print(f"[dry-run] '{ws.title}' row {sheet_row_num}, {ALT_TEXT_COL}:\n  -> {alt_text}")
        print(f"[dry-run] {len(updates)} rows would be written to '{ws.title}' -- nothing was actually written.")
        return

    import gspread
    batch = [
        {
            "range": gspread.utils.rowcol_to_a1(idx + 2, col_num),
            "values": [[alt_text]],
        }
        for idx, alt_text in updates.items()
    ]
    ws.batch_update(batch)
    print(
        f"Wrote {filled} rows to '{ws.title}' "
        f"({resumed} pulled from checkpoint, {filled - resumed} freshly generated)."
    )


def reconnaissance_tab(ws) -> None:
    """
    Cost-free inspection of one tab: no generation, no API calls, no
    writes. Reports whether this tab has the expected columns, how many
    rows have images, and samples a handful of image URLs spread across
    the tab so you can actually look at them before deciding whether the
    current prompt fits this course or needs a new DOMAIN module.
    """
    print(f"\n=== Tab: {ws.title} ===")
    values = ws.get_all_values()
    if not values:
        print("  Empty tab.")
        return

    header = values[0]
    rows = values[1:]
    print(f"  {len(rows)} data row(s). Header has {len(header)} columns.")

    has_images_col = IMAGES_COL in header
    has_alt_col = ALT_TEXT_COL in header
    print(f"  '{IMAGES_COL}' column present: {has_images_col}")
    print(f"  '{ALT_TEXT_COL}' column present: {has_alt_col}")

    missing_expected = [
        c for c in (PROBLEM_NAME_COL, ROW_TYPE_COL, HINT_ID_COL, TITLE_COL, BODY_COL)
        if c not in header
    ]
    if missing_expected:
        print(f"  [warn] missing expected column(s): {missing_expected} -- "
              f"this tab's layout may differ from Data 8's, double check before running generation")

    if not has_images_col:
        print("  Can't sample images -- no Images column found.")
        return

    img_idx = header.index(IMAGES_COL)
    rows_with_images = [r for r in rows if len(r) > img_idx and r[img_idx].strip()]
    print(f"  {len(rows_with_images)} of {len(rows)} rows have at least one image.")

    if not rows_with_images:
        return

    # Spread the sample across the tab (start, middle, end) rather than
    # just the first few, so you see variety in problem type.
    n_samples = min(5, len(rows_with_images))
    step = max(1, len(rows_with_images) // n_samples)
    sample = rows_with_images[::step][:n_samples]

    print(f"  Sample image URL(s) to look at:")
    for r in sample:
        urls = r[img_idx].split()
        title = r[header.index(TITLE_COL)] if TITLE_COL in header and len(r) > header.index(TITLE_COL) else ""
        print(f"    - {urls[0]}" + (f"  (Title: {title[:50]})" if title else ""))


def run_sheet_mode(args) -> None:
    """Entry point for --sheet-url: authenticates once, discovers every
    tab on the spreadsheet, and processes them one at a time in place."""
    import gspread

    spreadsheet_id = extract_spreadsheet_id(args.sheet_url)
    gc = gspread.service_account(filename=args.service_account)
    sh = gc.open_by_key(spreadsheet_id)

    worksheets = sh.worksheets()
    print(f"Found {len(worksheets)} tab(s) in '{sh.title}': {[ws.title for ws in worksheets]}")

    if args.reconnaissance:
        print("Running in --reconnaissance mode: no generation, no API calls, no writes.")
        for ws in worksheets:
            reconnaissance_tab(ws)
        print("\nDone. Open a few of the sampled image URLs above to decide on a prompt approach.")
        return

    client = OpenAI()
    if args.dry_run:
        print("Running in --dry-run mode: nothing will be written to the live sheet.")

    for ws in worksheets:
        process_tab(client, ws, spreadsheet_id, args)

    print("\nDone with all tabs.")


def main():
    global SYSTEM_PROMPT, MODEL
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", nargs="?", default=None,
                         help="CSV mode: path to an exported sheet CSV. Omit if using --sheet-url instead.")
    parser.add_argument("--sheet-url", default=None,
                         help="Sheet mode: URL of the live Google Sheet. Discovers and processes every "
                              "tab automatically -- no CSV export needed.")
    parser.add_argument("--dry-run", action="store_true",
                         help="Sheet mode only: generate and print what would be written, but don't "
                              "actually write anything to the live sheet.")
    parser.add_argument("--reconnaissance", action="store_true",
                         help="Sheet mode only: no generation, no API calls, no writes. Reports each "
                              "tab's column layout and samples a few image URLs so you can decide on a "
                              "prompt approach before running anything for real. Doesn't need an OpenAI "
                              "key.")
    parser.add_argument("--domain", choices=sorted(DOMAIN_PROMPTS), default="data-science",
                         help="course type, picks the course-specific part of the prompt. Checkpoints don't record "
                              "it, so use --force-refresh when rerunning a course with a different domain.")
    parser.add_argument("--model", default=MODEL,
                         help="OpenAI vision model. gpt-5.5 read graph coordinates far better than gpt-4o on "
                              "SJSU 1019S, but both still misread some labels, so review every draft.")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--limit", type=int, default=None,
                         help="only process the first N rows needing alt text (per tab, in sheet mode)")
    parser.add_argument("--force-refresh", action="store_true",
                         help="ignore checkpoint cache for blank rows and regenerate them")
    parser.add_argument("--refresh-key", action="append", default=[],
                         help="regenerate one specific row by its row_key hash, even if it "
                              "already has alt text. Repeatable.")
    parser.add_argument("--push-to-sheet", action="store_true",
                         help="CSV mode: also write newly-filled alt text directly into the live Google Sheet")
    parser.add_argument("--push-only", action="store_true",
                         help="CSV mode: skip generation entirely -- just push every row that already has "
                              "alt text in csv_path (e.g. a file you've hand-reviewed/edited). "
                              "Implies --push-to-sheet.")
    parser.add_argument("--spreadsheet-id", default=None)
    parser.add_argument("--worksheet-name", default=None)
    parser.add_argument("--service-account", default="credentials/service-account-credentials.json")
    args = parser.parse_args()

    SYSTEM_PROMPT = CORE_PROMPT + "\n" + DOMAIN_PROMPTS[args.domain]
    MODEL = args.model

    if bool(args.csv_path) == bool(args.sheet_url):
        print("[error] provide exactly one of: csv_path, or --sheet-url")
        sys.exit(1)

    if args.sheet_url:
        run_sheet_mode(args)
        return

    # ---- CSV mode (original workflow) --------------------------------
    csv_path = Path(args.csv_path)
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    if ALT_TEXT_COL not in df.columns:
        df[ALT_TEXT_COL] = ""
    df[PROBLEM_NAME_COL] = df[PROBLEM_NAME_COL].replace("", pd.NA).ffill().fillna("")

    if args.push_only:
        touched_indices = df.index[df[ALT_TEXT_COL].str.strip() != ""].tolist()
        print(f"--push-only: pushing {len(touched_indices)} rows with alt text from {csv_path} as-is (no API calls).")
        push_to_sheet(df, touched_indices, args)
        return

    checkpoint_path = csv_path.with_name(csv_path.stem + "_alt_text_checkpoint.json")
    checkpoint = Checkpoint(checkpoint_path)
    client = OpenAI()  # reads OPENAI_API_KEY from env

    refresh_keys = set(args.refresh_key)
    work_items, skipped_has_alt, skipped_no_image, unmatched = build_work_items(
        df, refresh_keys, args.force_refresh
    )
    for k in unmatched:
        print(f"[warn] --refresh-key {k} didn't match any row in this CSV -- check the hash")

    if args.limit:
        work_items = work_items[: args.limit]

    already_cached = sum(
        1 for _, key, _, _, force in work_items if not force and checkpoint.get(key) is not None
    )
    print(
        f"{len(work_items)} rows to process this run "
        f"({skipped_has_alt} already had alt text, {skipped_no_image} had no images). "
        f"{already_cached} will be pulled from checkpoint instead of re-calling the API."
    )

    updates, filled, resumed = run_work_items(client, checkpoint, work_items, args.workers)
    for idx, alt_text in updates.items():
        df.at[idx, ALT_TEXT_COL] = alt_text
    touched_indices = list(updates.keys())

    out_path = csv_path.with_name(csv_path.stem + "_with_alt_text.csv")
    df.to_csv(out_path, index=False, quoting=csv.QUOTE_ALL)

    print(
        f"\nDone. {filled} rows now have alt text this run "
        f"({resumed} pulled from checkpoint, {filled - resumed} freshly generated)."
    )
    print(f"Wrote: {out_path}")
    print(f"Checkpoint: {checkpoint_path} -- rerun the same command anytime to resume or pick up newly-blank rows.")

    if args.push_to_sheet:
        push_to_sheet(df, touched_indices, args)


if __name__ == "__main__":
    main()