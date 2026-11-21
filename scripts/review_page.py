"""
review_page.py

Builds an HTML page that shows each distinct image next to its drafted alt text and the sheet
rows that use it, so a reviewer can check every draft against its image before push_reviewed.py.
Edit any draft you change directly in the CSV.

    python review_page.py rows_with_alt_text.csv review.html
"""

import csv
import html
import sys
from collections import OrderedDict


def main():
    rows = list(csv.DictReader(open(sys.argv[1], newline="")))
    by_images = OrderedDict()
    for r in rows:
        by_images.setdefault(r["Images (space delimited)"], []).append(r)
    parts = ["<!doctype html><meta charset=utf-8><title>Alt text review</title>",
             "<style>body{font:15px/1.5 system-ui;max-width:1000px;margin:2em auto;padding:0 1em}"
             ".item{border-top:1px solid #ccc;padding:1em 0;display:grid;grid-template-columns:420px 1fr;gap:1.5em}"
             "img{max-width:420px;border:1px solid #eee;display:block;margin-bottom:.5em}"
             ".where{color:#666;font-size:13px}</style>",
             f"<h1>Alt text drafts</h1><p>{len(by_images)} distinct images across {len(rows)} sheet rows. "
             "Check each draft against its image. A row with several images has one description per image, "
             "separated by |.</p>"]
    for n, (images, rs) in enumerate(by_images.items(), 1):
        pics = "".join(f"<img src='{html.escape(u)}' alt=''>" for u in images.split())
        drafts = {r["Alt Text (pipe delimited)"] for r in rs}
        texts = "".join(f"<p>{html.escape(t) or '<i>(no draft)</i>'}</p>" for t in drafts)
        where = "; ".join(f"{r['Tab']} row {r['Sheet Row']}" for r in rs[:6])
        where += f"; and {len(rs) - 6} more" if len(rs) > 6 else ""
        parts.append(f"<div class=item><div>{pics}</div><div><b>{n}. {html.escape(rs[0]['Title'])}</b> "
                     f"({html.escape(rs[0]['Row Type'])}){texts}<div class=where>Used in: {html.escape(where)}</div></div></div>")
    open(sys.argv[2], "w").write("\n".join(parts))
    print(f"{len(by_images)} images -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
