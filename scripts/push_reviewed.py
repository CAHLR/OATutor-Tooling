"""
push_reviewed.py

Writes reviewed alt text from a combined CSV (one row per sheet row with images, with
"Tab" and "Sheet Row" columns, as exported for SJSU 1019S) into the live sheet's
"Alt Text (pipe delimited)" column.

A row is written only if the live row still has the same Problem Name, Row Type and
Images as the CSV, and its alt text cell is empty. Anything else is skipped and listed,
so a sheet edited since the export never gets alt text in the wrong row and hand-written
alt text is never overwritten.

Dry run by default (read-only credentials, nothing written). Add --write to write.

    python scripts/push_reviewed.py data/sjsu1019s/sjsu1019s_image_rows_with_alt_text.csv \
        --spreadsheet-id <id> [--write]
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict

import gspread
from google.oauth2.service_account import Credentials

ALT_TEXT_COL = "Alt Text (pipe delimited)"
CHECK_COLS = ["Problem Name", "Row Type", "Images (space delimited)"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--spreadsheet-id", required=True)
    parser.add_argument("--service-account", default="credentials/service-account-credentials.json")
    parser.add_argument("--write", action="store_true", help="actually write; without it, only report")
    args = parser.parse_args()

    scope = "spreadsheets" if args.write else "spreadsheets.readonly"
    creds = Credentials.from_service_account_file(
        args.service_account, scopes=[f"https://www.googleapis.com/auth/{scope}"])
    sh = gspread.authorize(creds).open_by_key(args.spreadsheet_id)

    by_tab = defaultdict(list)
    for row in csv.DictReader(open(args.csv_path, newline="")):
        if row[ALT_TEXT_COL].strip():
            by_tab[row["Tab"]].append(row)

    written = skipped = 0
    for tab, rows in by_tab.items():
        ws = sh.worksheet(tab)
        values = ws.get_all_values()
        header = values[0]
        if ALT_TEXT_COL not in header:
            print(f"[skip] '{tab}' has no '{ALT_TEXT_COL}' column ({len(rows)} rows)")
            skipped += len(rows)
            continue
        alt_idx = header.index(ALT_TEXT_COL)
        updates = []
        for row in rows:
            n = int(row["Sheet Row"])
            live = values[n - 1] if n - 1 < len(values) else []
            cell = lambda col: live[header.index(col)].strip() if header.index(col) < len(live) else ""
            # the CSV carries Problem Name forward onto rows where the sheet leaves it blank
            mismatched = [c for c in CHECK_COLS if cell(c) and cell(c) != row[c].strip()]
            if not live or mismatched:
                print(f"[skip] '{tab}' row {n}: live row differs on {mismatched or 'everything'}")
                skipped += 1
                continue
            if cell(ALT_TEXT_COL):
                print(f"[skip] '{tab}' row {n}: already has alt text, leaving it")
                skipped += 1
                continue
            updates.append({"range": gspread.utils.rowcol_to_a1(n, alt_idx + 1), "values": [[row[ALT_TEXT_COL]]]})
        verb = "wrote" if args.write else "would write"
        cells = ", ".join(u["range"] for u in updates)
        print(f"'{tab}': {verb} {len(updates)} cells ({cells})")
        if args.write and updates:
            ws.batch_update(updates)
        written += len(updates)

    print(f"\n{'Wrote' if args.write else 'Dry run: would write'} {written} cells, skipped {skipped}.")


if __name__ == "__main__":
    main()
