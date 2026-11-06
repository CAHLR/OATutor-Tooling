# Alt text scripts

Scripts that fill the optional `Alt Text (pipe delimited)` column of a content sheet. The
content script turns that column into `figureAlts` in the problem JSON, and OATutor renders it
as each image's alt text.

Started by Natalie Jaramillo (summer 2026, `generate_alt_text.py`); extended by Noel Sason.

## Setup

Run everything from this folder.

```bash
pip install -r requirements.txt
```

- `.env` here with `OPENAI_API_KEY=...` (only `generate_alt_text.py` needs it).
- `credentials/service-account-credentials.json`: a Google service account key, for reading
  and writing sheets. Share each sheet with the account's `client_email` (Viewer to read,
  Editor to write). Both are ignored by git; never commit them.

## Where the column goes

Put `Alt Text (pipe delimited)` in an empty column. Any position works: the content script
reads it by name and finds the validator columns by their `Validator Check` header. One
entry per image, in the same order as `Images (space delimited)`, separated by `|`.

If you insert a column on a sheet the content script has already validated, check row 1 afterward
for a repeated header (for example two `Image Checksum` cells). A repeated header makes
every problem on that tab fail validation. Clear the stale one.

## Scripts

**`generate_alt_text.py`** drafts alt text with an OpenAI vision model.

```bash
python generate_alt_text.py rows.csv --domain algebra --model gpt-5.5
```

- `--domain` picks the course-specific part of the prompt: `data-science` (tables, code,
  plots; used for Data 8 and Data 100) or `algebra` (number lines, counters, function
  graphs, charts).
- In CSV mode it writes only a local `rows_with_alt_text.csv`; nothing goes to the sheet.
  Sheet mode (`--sheet-url`) writes straight into the live sheet unless you pass `--dry-run`.
- Each image URL is described once per run, so a reused image gets the same text everywhere.
  If any image in a row fails, the whole row stays blank, because the content script pairs
  the Nth alt text with the Nth image.

**Review every draft against its image before it goes into a sheet.** On SJSU 1019S,
gpt-4o misread every coordinate on a graph, and gpt-5.5 once merged two adjacent labels
into a wrong mixed number.

**`push_reviewed.py`** writes reviewed drafts from a CSV that has `Tab` and `Sheet Row`
columns into the live sheet. It fills only empty cells, and only on rows whose Problem
Name, Row Type and Images still match. Dry run unless `--write`.

**`import_sf_alt_text.py`** copied Jennifer Kamrin's hand-written Solid Foundations alt
text (her `images` table: `filename`, `alt_text`) into the Trigonometry and Algebra
sheets, matching each image link to a row by file name. Entries with known errors are
listed in `HOLD` and left blank. Dry run unless `--write`; with `--write` it diffs the sheet
before and after and checks that only the planned cells changed.
