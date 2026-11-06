"""
import_sf_alt_text.py

Copies Jennifer Kamrin's hand-written Solid Foundations alt text (her "images" table:
filename, alt_text, ...) into the OATutor content sheets' "Alt Text (pipe delimited)"
column, matching each image link to a table row by the file name at the end of the link
(e.g. https://i.postimg.cc/RFtzcjRW/trig1-prob1.jpg -> trig1-prob1).

The header goes into the empty spacer column just left of "Validator Check" instead of a
newly inserted column, so the validator columns don't move. A tab is skipped if that
column isn't an empty, unnamed column.

A row is filled only if its alt text cell is empty and every image in it has usable alt
text; otherwise it stays blank, because the tooling pairs the Nth alt text with the Nth
image. Entries in HOLD (questioned, waiting on the author) are treated as unusable.

Dry run by default. With --write it snapshots each sheet, writes, re-reads, and checks
that exactly the planned cells changed.

    python scripts/import_sf_alt_text.py --alt-table <id> --sheet <id> [--sheet <id>] [--write]
"""

from __future__ import annotations

import argparse
import re
import time
from collections import Counter

import gspread
from google.oauth2.service_account import Credentials

ALT_TEXT_COL = "Alt Text (pipe delimited)"
IMAGES_COL = "Images (space delimited)"
VALIDATOR_COL = "Validator Check"
SKIP_TABS = {"TEST"}
# Entries that contradict themselves or the math; sent back to the author to confirm.
HOLD = {"trig3-prob2a", "trig3-prob2b", "trig3-prob2c", "trig121-prob6", "trig321-prob2",
        "fractionmultiplication-2"}


def norm(name: str) -> str:
    """Link file names and table names differ in extension and _ vs - (postimg rewrites _)."""
    return re.sub(r"\.(png|jpe?g|gif|svg|webp)$", "", name.strip().lower()).replace("_", "-")


def read_all(gc, key):
    for attempt in range(6):
        try:
            sh = gc.open_by_key(key)
            titles = [ws.title for ws in sh.worksheets()]
            vrs = sh.values_batch_get([f"'{t}'" for t in titles])["valueRanges"]
            return sh, {t: vr.get("values", []) for t, vr in zip(titles, vrs)}
        except gspread.exceptions.APIError as e:
            if "429" not in str(e):
                raise
            time.sleep(30)
    raise RuntimeError("rate limited")


def plan_tab(tab, values, alt_by_name):
    """Returns (header cell or None, [(row, text)], notes)."""
    if not values or IMAGES_COL not in values[0]:
        return None, [], []
    header = values[0]
    img = header.index(IMAGES_COL)
    rows = [(n, r) for n, r in enumerate(values[1:], start=2) if img < len(r) and r[img].strip()]
    if not rows:
        return None, [], []
    if ALT_TEXT_COL in header:
        alt_col, header_cell = header.index(ALT_TEXT_COL), None
    else:
        if VALIDATOR_COL not in header:
            return None, [], [f"no '{VALIDATOR_COL}' column, skipped"]
        alt_col = header.index(VALIDATOR_COL) - 1
        if header[alt_col].strip() or any(alt_col < len(r) and r[alt_col].strip() for r in values[1:]):
            return None, [], [f"column {alt_col + 1} before '{VALIDATOR_COL}' isn't empty, skipped"]
        header_cell = (1, alt_col + 1)
    cells, notes = [], []
    for n, r in rows:
        if alt_col < len(r) and r[alt_col].strip():
            notes.append(f"row {n}: already has alt text, left alone")
            continue
        names = [norm(u.rstrip("/").split("/")[-1]) for u in r[img].split()]
        missing = [x for x in names if x not in alt_by_name or not alt_by_name[x].strip()]
        held = [x for x in names if x in HOLD]
        if missing or held:
            notes.append(f"row {n}: left blank ({'held: ' + ', '.join(held) if held else 'no alt text for: ' + ', '.join(missing)})")
            continue
        cells.append((n, alt_col + 1, " | ".join(alt_by_name[x] for x in names)))
    return header_cell, cells, notes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alt-table", required=True, help="spreadsheet id of the copy of J. Kamrin's images table")
    parser.add_argument("--sheet", action="append", required=True, help="content spreadsheet id (repeatable)")
    parser.add_argument("--service-account", default="credentials/service-account-credentials.json")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    creds = Credentials.from_service_account_file(
        args.service_account, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)

    _, table_tabs = read_all(gc, args.alt_table)
    table = table_tabs["images"]
    h = table[0]
    fn, at = h.index("filename"), h.index("alt_text")
    alt_by_name = {norm(r[fn]): (r[at] if at < len(r) else "") for r in table[1:] if fn < len(r) and r[fn].strip()}
    piped = [k for k, v in alt_by_name.items() if "|" in v]
    if piped:
        raise SystemExit(f"alt text contains '|', which the tooling splits on: {piped}")

    for key in args.sheet:
        sh, before = read_all(gc, key)
        print(f"\n=== {sh.title}")
        updates, expected, totals = [], {}, Counter()
        for tab, values in before.items():
            if tab in SKIP_TABS:
                continue
            header_cell, cells, notes = plan_tab(tab, values, alt_by_name)
            if not (header_cell or cells or notes):
                continue
            if header_cell:
                updates.append((tab, *header_cell, ALT_TEXT_COL))
            updates += [(tab, n, c, text) for n, c, text in cells]
            totals["rows"] += len(cells)
            totals["blank"] += sum(1 for x in notes if "left blank" in x)
            if any("skipped" in x for x in notes):
                print(f"  {tab}: SKIPPED, {notes[0]}")
                continue
            print(f"  {tab}: header {gspread.utils.rowcol_to_a1(*header_cell) if header_cell else '(exists)'}, "
                  f"{len(cells)} rows to fill" + "".join(f"\n      {x}" for x in notes))
        for tab, r, c, text in updates:
            expected[(tab, r, c)] = text
        print(f"  total: {totals['rows']} rows to fill, {totals['blank']} left blank, "
              f"{sum(1 for u in updates if u[3] == ALT_TEXT_COL)} header cells")
        if not args.write or not updates:
            continue

        sh.values_batch_update({"valueInputOption": "RAW", "data": [
            {"range": f"'{tab}'!{gspread.utils.rowcol_to_a1(r, c)}", "values": [[text]]} for tab, r, c, text in updates]})
        time.sleep(5)
        _, after = read_all(gc, key)
        changed = {}
        for tab in before:
            b, a = before[tab], after.get(tab, [])
            for i in range(max(len(b), len(a))):
                rb, ra = (b[i] if i < len(b) else []), (a[i] if i < len(a) else [])
                for j in range(max(len(rb), len(ra))):
                    vb, va = (rb[j] if j < len(rb) else ""), (ra[j] if j < len(ra) else "")
                    if vb != va:
                        changed[(tab, i + 1, j + 1)] = va
        print(f"  verify: {len(changed)} cells changed; exactly the planned cells with the exact text: {changed == expected}")
        for k in set(changed) ^ set(expected):
            print("    UNEXPECTED", k)


if __name__ == "__main__":
    main()
