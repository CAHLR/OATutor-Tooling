"""
export_image_rows.py

Read-only: writes every row that has an image, from every tab (or the tabs you name), into one
CSV with "Tab" and "Sheet Row" columns. That CSV is the input for generate_alt_text.py (CSV mode),
review_page.py and push_reviewed.py. One CSV per spreadsheet means an image reused across tabs is
described once and reads the same everywhere.

    python export_image_rows.py <spreadsheet id> out.csv [--tab "Disc2" --tab "Disc3"]
"""

import argparse
import csv

import gspread
from google.oauth2.service_account import Credentials

COLS = ["Problem Name", "Row Type", "HintID", "Title", "Body Text", "Images (space delimited)",
        "Alt Text (pipe delimited)"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spreadsheet_id")
    parser.add_argument("out_csv")
    parser.add_argument("--tab", action="append", help="only these tabs (repeatable)")
    parser.add_argument("--service-account", default="credentials/service-account-credentials.json")
    args = parser.parse_args()

    creds = Credentials.from_service_account_file(
        args.service_account, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    sh = gspread.authorize(creds).open_by_key(args.spreadsheet_id)
    tabs = [ws.title for ws in sh.worksheets() if not args.tab or ws.title in args.tab]
    count = 0
    with open(args.out_csv, "w", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["Tab", "Sheet Row"] + COLS)
        for tab, vr in zip(tabs, sh.values_batch_get([f"'{t}'" for t in tabs])["valueRanges"]):
            values = vr.get("values", [])
            if not values:
                continue
            header = values[0]
            get = lambda r, c: r[header.index(c)] if c in header and header.index(c) < len(r) else ""
            name = ""
            for n, r in enumerate(values[1:], start=2):
                name = get(r, "Problem Name") or name  # carried forward onto rows that leave it blank
                if get(r, "Images (space delimited)").strip():
                    w.writerow([tab, n, name] + [get(r, c) for c in COLS[1:]])
                    count += 1
    print(f"{count} image rows from {len(tabs)} tabs -> {args.out_csv}")


if __name__ == "__main__":
    main()
