"""
Fill BKT parameters for disqualified KCs using donor averages.

Phase 1 of the BKT parameter implementation (see
notes/bkt-implementation/implementation_plan.md). For every disqualified KC
(Tier 1 + Tier 2) that exists in OATutor-Content's experimentalBKTParams.json,
overwrite its untrustworthy fitted params with a donor average:

    if the KC's subject has >= MIN_DONORS approved donors:
        use that subject's donor mean   (most-donor subject if multi-subject)
    else:
        use the global donor mean (all Tier 3+4 donors)

Donors  = Tier 3 (Keep w/ Notation) + Tier 4 (Clean)   -> 89 KCs
Recipients = Tier 1 (Hard Disqualify) + Tier 2 (Disqualify), restricted to the
             28 that are present in experimentalBKTParams.json.

Writes the updated JSON into the OATutor-Content working tree, emits a
provenance CSV, and validates every written value. defaultBKTParams.json is
never touched. Use --dry-run to preview without writing.
"""
import argparse
import json
import os
from collections import Counter, defaultdict

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIFICATION_XLSX = os.path.join(
    SCRIPT_DIR, "..", "notes", "reports", "kc_final_report_with_qualifications.xlsx"
)
CLASSIFICATION_SHEET = "Final KC Report"
PROVENANCE_CSV = os.path.join(
    SCRIPT_DIR, "..", "notes", "reports", "phase1_fill_provenance.csv"
)

MIN_DONORS = 5
DONOR_TIERS = (3, 4)        # Keep w/ Notation, Clean
RECIPIENT_TIERS = (1, 2)    # Hard Disqualify, Disqualify

# Classification-sheet column -> experimentalBKTParams.json field
PARAM_COLS = {
    "Prior":    "probMastery",
    "pTransit": "probTransit",
    "pSlip":    "probSlip",
    "pGuess":   "probGuess",
}


def resolve_content_repo():
    """Locate the OATutor-Content repo. The sibling-path convention used by
    fit_bkt.py ("../../OATutor-Content") is machine-specific, so try an env var
    override and a couple of known locations, and fail loudly if none exist."""
    candidates = []
    if os.environ.get("OATUTOR_CONTENT"):
        candidates.append(os.environ["OATUTOR_CONTENT"])
    candidates += [
        os.path.join(SCRIPT_DIR, "..", "..", "OATutor-Content"),
        os.path.expanduser("~/OATutor-Content"),
    ]
    for c in candidates:
        if os.path.isfile(os.path.join(c, "bkt-params", "experimentalBKTParams.json")):
            return os.path.normpath(c)
    raise FileNotFoundError(
        "Could not locate OATutor-Content (need bkt-params/experimentalBKTParams.json). "
        "Set the OATUTOR_CONTENT environment variable to its path. Tried:\n  "
        + "\n  ".join(os.path.normpath(c) for c in candidates)
    )


def subject_of(course_name):
    """Collapse a coursePlans courseName into a subject area."""
    c = course_name.lower()
    if "physics" in c:
        return "Physics"
    if "stat" in c:
        return "Statistics"
    if "calc" in c or "1019" in c:   # Calculus, Pre-Calculus, SJSU 1019/1019S (precalc)
        return "Calc/PreCalc"
    if "matematik" in c:
        return "Other"
    if "alg" in c or "1018" in c:
        return "Algebra"
    return "Other"


def build_kc_subjects(course_plans):
    """KC -> set of subject areas, from each lesson's learningObjectives."""
    kc_subjects = defaultdict(set)
    for course in course_plans:
        subj = subject_of(course["courseName"])
        for lesson in course["lessons"]:
            for kc in (lesson.get("learningObjectives") or {}):
                kc_subjects[kc].add(subj)
    return kc_subjects


def compute_donor_means(donors):
    """Return (global_mean, subject_means, donor_counts).

    global_mean: mean over all donors (decided: "global means global").
    subject_means / donor_counts: per subject, over donors mapped to that subject
    (these are inherently the coursePlans-mapped, in-JSON donors)."""
    global_mean = {col: float(donors[col].mean()) for col in PARAM_COLS}

    donor_counts = Counter()
    for subs in donors["subjects"]:
        for s in subs:
            donor_counts[s] += 1

    subject_means = {}
    for s in donor_counts:
        mask = donors["subjects"].apply(lambda L: s in L)
        subject_means[s] = {col: float(donors[mask][col].mean()) for col in PARAM_COLS}

    return global_mean, subject_means, donor_counts


def resolve_fill(subjects, global_mean, subject_means, donor_counts):
    """Pick the fill vector for one recipient. Domain mean when the subject has
    >= MIN_DONORS donors (most-donor subject if multiple qualify); else global."""
    qualifying = [s for s in subjects if donor_counts.get(s, 0) >= MIN_DONORS]
    if qualifying:
        chosen = max(qualifying, key=lambda s: donor_counts[s])
        return subject_means[chosen], chosen, "domain_avg"
    return global_mean, "GLOBAL", "global_avg"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="compute and report, but do not write the JSON")
    args = ap.parse_args()

    content_repo = resolve_content_repo()
    params_path = os.path.join(content_repo, "bkt-params", "experimentalBKTParams.json")
    course_plans_path = os.path.join(content_repo, "coursePlans.json")
    print(f"Content repo: {content_repo}")

    # ── Load ────────────────────────────────────────────────────────────────
    clf = pd.read_excel(os.path.normpath(CLASSIFICATION_XLSX), sheet_name=CLASSIFICATION_SHEET)
    with open(params_path) as f:
        bkt = json.load(f)
    with open(course_plans_path) as f:
        course_plans = json.load(f)

    kc_subjects = build_kc_subjects(course_plans)
    clf["subjects"] = clf["KC"].apply(lambda k: sorted(kc_subjects.get(k, set())))

    # ── Donor means ─────────────────────────────────────────────────────────
    donors = clf[clf["Tier"].isin(DONOR_TIERS)].copy()
    global_mean, subject_means, donor_counts = compute_donor_means(donors)
    print(f"\nDonors: {len(donors)} (Tier {DONOR_TIERS})")
    print(f"  donor counts by subject: {dict(donor_counts)}")
    print(f"  global mean: { {k: round(v, 4) for k, v in global_mean.items()} }")
    for s in sorted(subject_means):
        if donor_counts[s] >= MIN_DONORS:
            print(f"  {s} mean (n={donor_counts[s]}): "
                  f"{ {k: round(v, 4) for k, v in subject_means[s].items()} }")

    # ── Resolve fills for writable recipients ────────────────────────────────
    recipients = clf[clf["Tier"].isin(RECIPIENT_TIERS)].copy()
    in_json = recipients[recipients["KC"].isin(bkt)]
    skipped = sorted(set(recipients["KC"]) - set(in_json["KC"]))
    print(f"\nRecipients: {len(recipients)} (Tier {RECIPIENT_TIERS}) | "
          f"writable (in JSON): {len(in_json)} | skipped (other repos): {len(skipped)}")
    if skipped:
        print(f"  skipped: {skipped}")

    rows = []
    for _, r in in_json.iterrows():
        vec, subj, source = resolve_fill(r["subjects"], global_mean, subject_means, donor_counts)
        old = {field: bkt[r["KC"]][field] for field in PARAM_COLS.values()}
        new = {field: round(vec[col], 6) for col, field in PARAM_COLS.items()}
        rows.append({
            "KC": r["KC"], "tier": int(r["Tier"]), "fill_source": source,
            "fill_subject": subj,
            **{f"old_{f}": old[f] for f in PARAM_COLS.values()},
            **{f"new_{f}": new[f] for f in PARAM_COLS.values()},
        })
        if not args.dry_run:
            bkt[r["KC"]].update(new)

    prov = pd.DataFrame(rows).sort_values(["fill_subject", "KC"])
    print(f"\nFill source breakdown: {dict(Counter(prov['fill_source']))}")
    print(f"Fill subject breakdown: {dict(Counter(prov['fill_subject']))}")

    # ── Validate every written value ──────────────────────────────────────────
    problems = []
    for _, r in prov.iterrows():
        vals = {f: r[f"new_{f}"] for f in PARAM_COLS.values()}
        if any(not (0.0 <= v <= 1.0) for v in vals.values()):
            problems.append(f"{r['KC']}: param out of [0,1] -> {vals}")
        if vals["probSlip"] + vals["probGuess"] >= 1.0:
            problems.append(f"{r['KC']}: slip+guess >= 1 -> {vals}")
    if problems:
        raise ValueError("Validation failed:\n  " + "\n  ".join(problems))
    print(f"\nValidation OK: all {len(prov)} fills in [0,1] and slip+guess < 1.")

    # ── Write ─────────────────────────────────────────────────────────────────
    prov.to_csv(os.path.normpath(PROVENANCE_CSV), index=False)
    print(f"Provenance -> {os.path.normpath(PROVENANCE_CSV)}")

    if args.dry_run:
        print("\n[dry-run] experimentalBKTParams.json NOT modified.")
    else:
        with open(params_path, "w") as f:
            json.dump(bkt, f, indent=2)
        print(f"\nWrote {len(prov)} updated KCs -> {params_path}")
        print("defaultBKTParams.json untouched.")


if __name__ == "__main__":
    main()
