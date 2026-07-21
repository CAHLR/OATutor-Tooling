"""
Write fitted BKT parameters and fill disqualified KCs (see
notes/bkt-implementation/implementation_plan.md and the approved plan).

This produces *new* JSON files under bkt/output/ (nothing is edited in place):

  bkt/output/experimentalBKTParams.json   full OATutor-Content file + 105 updates
  bkt/output/<repo>BKTParams.json         one per external repo (Chem/Calbright)

so each can be `git diff`'d against its repo copy and placed by hand.

For the 125 classified KCs (notes/reports/kc_final_report_with_qualifications.xlsx):

  Donors    = Tier 3 (Keep w/ Notation) + Tier 4 (Clean)   -> 89 KCs, fitted values
  Recipients = Tier 1 (Hard Disqualify) + Tier 2 (Disqualify) -> 36 KCs, donor-average fill

  - 105 land in OATutor-Content (76 donors + 29 recipients). 7 of those were
    renamed upstream with an "_in_openstax_precalc" suffix (see RENAMES); we map
    the old fitted name -> the new JSON key.
  - Recipient fill: domain average when the KC's subject has >= MIN_DONORS donors
    (most-donor subject if multi-subject), else the global donor mean (all 89).
    Physics recipients have no donors -> global. Data Science clears MIN_DONORS.
  - 20 KCs live in other repos: Chemistry (Chem1A/Chem49/Chemistry) and Calbright
    get their own output files (donors fitted; Chem recipients -> Chemistry domain
    mean; Calbright/Swedish recipients left at default). Swedish has no repo.

defaultBKTParams.json is never touched. Source files are fetched from the current
CAHLR remote (the local checkout is stale); use --content-ref to pin a ref.
"""
import argparse
import json
import os
import urllib.request
from collections import Counter, defaultdict

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIFICATION_XLSX = os.path.join(
    SCRIPT_DIR, "..", "notes", "reports", "kc_final_report_with_qualifications.xlsx"
)
CLASSIFICATION_SHEET = "Final KC Report"
FITTED_CSV = os.path.join(SCRIPT_DIR, "data", "fitted_params_hint_adjusted.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
PROVENANCE_CSV = os.path.join(
    SCRIPT_DIR, "..", "notes", "reports", "phase1_fill_provenance.csv"
)

MIN_DONORS = 5
DONOR_TIERS = (3, 4)        # Keep w/ Notation, Clean
RECIPIENT_TIERS = (1, 2)    # Hard Disqualify, Disqualify

# fitted_params_hint_adjusted.csv `param` -> experimentalBKTParams.json field
PARAM_FIELDS = {
    "prior":   "probMastery",
    "learns":  "probTransit",
    "slips":   "probSlip",
    "guesses": "probGuess",
}
FIELDS = list(PARAM_FIELDS.values())

# Classified KCs renamed upstream (suffix "_in_openstax_precalc"). The fitted CSV
# and classification sheet use the old name; the live JSON / coursePlans use the new.
RENAMES = {k: k + "_in_openstax_precalc" for k in (
    "representing_functions_using_tables",
    "evaluation_of_functions_in_algebra_forms",
    "evaluating_a_function_given_in_tabular_form",
    "evaluating_functions_expressed_in_formulas",
    "using_function_notation",
    "using_the_horizontal_line_test",
    "using_the_vertical_line_test",
)}

CAHLR_RAW = "https://raw.githubusercontent.com/CAHLR/{repo}/{ref}/{path}"
CONTENT_REPO = "OATutor-Content"
FORK_PARAMS_PATH = "src/content-sources/oatutor/bkt-params/{file}"

# External repos: which classified KCs map where. Donors get fitted values;
# `recipients` are filled from the Chemistry domain mean; `recipients_default`
# are left at the repo's existing default (per the approved plan).
EXTERNAL_REPOS = {
    "OATutor-Chem1A": {
        "file": "experimentalBKTParams.json",
        "donors": ["module_a", "module_b", "module_c", "module_d",
                   "module_f", "module_g", "module_h"],
        "recipients": [],
        "recipients_default": [],
    },
    "OATutor-Chem49": {
        "file": "experimentalBKTParams.json",
        "donors": ["stoichiometry"],
        "recipients": ["quantum", "thermo"],
        "recipients_default": [],
    },
    "OATutor-Chemistry": {
        "file": "experimentalBKTParams.json",
        "donors": ["stoichiometry"],
        "recipients": ["post_test", "pre_test"],
        "recipients_default": [],
    },
    "OATutor-CalbrightContent": {
        "file": "experimentalBKTParams.json",
        "donors": ["intermediate_sql", "professional_learning", "spreadsheets", "sql"],
        "recipients": [],
        "recipients_default": ["foundational_math"],
    },
}
# Chemistry domain mean is computed from these donors (across the chem repos).
CHEM_DONORS = ["module_a", "module_b", "module_c", "module_d", "module_f",
               "module_g", "module_h", "stoichiometry"]
# No repo in the CAHLR fork list; recorded for provenance only.
SWEDISH_DONORS = ["kedjeregeln"]
SWEDISH_RECIPIENTS_DEFAULT = ["derivator_av_trigonometriska_funktioner",
                              "evaluation_of_functions_in_algebraic_forms"]


def fetch_json(repo, path, ref):
    url = CAHLR_RAW.format(repo=repo, ref=ref, path=path)
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read())


def subject_of(course_name):
    """Collapse a coursePlans courseName into a subject area."""
    c = course_name.lower()
    if "physics" in c:
        return "Physics"
    if "stat" in c:
        return "Statistics"
    if "data" in c:                  # Data 8 Discussion Worksheets
        return "DataScience"
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


def load_fitted(path):
    """KC (old name) -> {field: value} from the long-format fitted CSV."""
    df = pd.read_csv(path)
    df = df[df["param"].isin(PARAM_FIELDS)]
    fitted = {}
    for skill, grp in df.groupby("skill"):
        vec = {PARAM_FIELDS[p]: float(v)
               for p, v in zip(grp["param"], grp["value"])}
        if set(vec) == set(FIELDS):
            fitted[skill] = vec
    return fitted


def mean_vec(vectors):
    n = len(vectors)
    return {f: round(sum(v[f] for v in vectors) / n, 6) for f in FIELDS}


def round_vec(vec):
    return {f: round(vec[f], 6) for f in FIELDS}


def validate(kc, vec):
    if any(not (0.0 <= vec[f] <= 1.0) for f in FIELDS):
        return f"{kc}: param out of [0,1] -> {vec}"
    if vec["probSlip"] + vec["probGuess"] >= 1.0:
        return f"{kc}: slip+guess >= 1 -> {vec}"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--content-ref", default="main",
                    help="git ref of CAHLR repos to fetch (default: main)")
    ap.add_argument("--dry-run", action="store_true",
                    help="compute and report, but do not write any output files")
    args = ap.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Load ──────────────────────────────────────────────────────────────────
    clf = pd.read_excel(os.path.normpath(CLASSIFICATION_XLSX),
                        sheet_name=CLASSIFICATION_SHEET)
    fitted = load_fitted(FITTED_CSV)
    print(f"Fitting from current CAHLR ref: {args.content_ref}")
    bkt = fetch_json(CONTENT_REPO, "bkt-params/experimentalBKTParams.json", args.content_ref)
    course_plans = fetch_json(CONTENT_REPO, "coursePlans.json", args.content_ref)
    print(f"Remote {CONTENT_REPO} experimental: {len(bkt)} KCs | "
          f"coursePlans: {len(course_plans)} courses")

    kc_subjects = build_kc_subjects(course_plans)
    clf["remote_name"] = clf["KC"].map(lambda k: RENAMES.get(k, k))
    clf["subjects"] = clf["remote_name"].map(lambda k: sorted(kc_subjects.get(k, set())))

    rows = []          # provenance rows
    problems = []      # validation failures (only over written values)

    def record(kc, remote_name, repo, tier, role, fill_source, subject, old, new, written):
        rows.append({
            "KC": kc, "remote_name": remote_name, "repo": repo, "tier": int(tier),
            "role": role, "fill_source": fill_source, "subject": subject,
            "written": written,
            **{f"old_{f}": (old or {}).get(f) for f in FIELDS},
            **{f"new_{f}": new[f] for f in FIELDS},
        })
        if written:
            p = validate(remote_name, new)
            if p:
                problems.append(p)

    # ── Donor means (global = all 89 donors; per-subject = Content donors) ─────
    donors = clf[clf["Tier"].isin(DONOR_TIERS)]
    global_mean = mean_vec([fitted[k] for k in donors["KC"]])

    content_donors = donors[donors["remote_name"].isin(bkt)]
    donor_counts = Counter()
    subject_vectors = defaultdict(list)
    for _, r in content_donors.iterrows():
        for s in r["subjects"]:
            donor_counts[s] += 1
            subject_vectors[s].append(fitted[r["KC"]])
    subject_means = {s: mean_vec(v) for s, v in subject_vectors.items()}

    print(f"\nDonors: {len(donors)} total | in Content: {len(content_donors)}")
    print(f"  donor counts by subject: {dict(donor_counts)}")
    print(f"  global mean (n=89): {global_mean}")
    for s in sorted(subject_means):
        if donor_counts[s] >= MIN_DONORS:
            print(f"  {s} mean (n={donor_counts[s]}): {subject_means[s]}")

    # ── OATutor-Content: write donor fitted values ────────────────────────────
    for _, r in content_donors.iterrows():
        new = round_vec(fitted[r["KC"]])
        old = bkt.get(r["remote_name"])
        record(r["KC"], r["remote_name"], CONTENT_REPO, r["Tier"], "donor",
               "fit", ",".join(r["subjects"]), old, new, written=True)
        bkt[r["remote_name"]] = new

    # ── OATutor-Content: fill recipients ──────────────────────────────────────
    recipients = clf[clf["Tier"].isin(RECIPIENT_TIERS)]
    content_recip = recipients[recipients["remote_name"].isin(bkt)]
    for _, r in content_recip.iterrows():
        qualifying = [s for s in r["subjects"] if donor_counts.get(s, 0) >= MIN_DONORS]
        if qualifying:
            chosen = max(qualifying, key=lambda s: donor_counts[s])
            new, source, subject = round_vec(subject_means[chosen]), "domain_avg", chosen
        else:
            new, source, subject = round_vec(global_mean), "global_avg", "GLOBAL"
        old = bkt.get(r["remote_name"])
        record(r["KC"], r["remote_name"], CONTENT_REPO, r["Tier"], "recipient",
               source, subject, old, new, written=True)
        bkt[r["remote_name"]] = new

    n_content = len(content_donors) + len(content_recip)
    print(f"\nOATutor-Content updates: {n_content} "
          f"({len(content_donors)} donors + {len(content_recip)} recipients)")

    # ── External repos ────────────────────────────────────────────────────────
    chem_mean = mean_vec([fitted[k] for k in CHEM_DONORS])
    print(f"Chemistry domain mean (n={len(CHEM_DONORS)}): {chem_mean}")
    tier_of = dict(zip(clf["KC"], clf["Tier"]))

    external_files = {}
    for repo, spec in EXTERNAL_REPOS.items():
        repo_json = fetch_json(repo, FORK_PARAMS_PATH.format(file=spec["file"]),
                               args.content_ref)
        for kc in spec["donors"]:
            new = round_vec(fitted[kc])
            present = kc in repo_json
            record(kc, kc, repo, tier_of[kc], "donor", "fit", "", repo_json.get(kc),
                   new, written=present)
            if present:
                repo_json[kc] = new
            else:
                print(f"  WARN {repo}: donor {kc} absent from repo file, skipped")
        for kc in spec["recipients"]:
            new = round_vec(chem_mean)
            present = kc in repo_json
            record(kc, kc, repo, tier_of[kc], "recipient", "domain_avg", "Chemistry",
                   repo_json.get(kc), new, written=present)
            if present:
                repo_json[kc] = new
            else:
                print(f"  WARN {repo}: recipient {kc} absent from repo file, skipped")
        for kc in spec["recipients_default"]:
            record(kc, kc, repo, tier_of[kc], "recipient", "left_default", "",
                   repo_json.get(kc), repo_json.get(kc, {f: None for f in FIELDS}),
                   written=False)
        external_files[repo] = repo_json
        print(f"  {repo}: {len(spec['donors'])} donors, "
              f"{len(spec['recipients'])} filled, "
              f"{len(spec['recipients_default'])} left default")

    # Swedish: no repo to write; record for provenance only.
    for kc in SWEDISH_DONORS:
        record(kc, kc, "Swedish(no-repo)", tier_of[kc], "donor", "no_repo", "",
               None, round_vec(fitted[kc]), written=False)
    for kc in SWEDISH_RECIPIENTS_DEFAULT:
        record(kc, kc, "Swedish(no-repo)", tier_of[kc], "recipient", "left_default", "",
               None, {f: None for f in FIELDS}, written=False)
    print("  Swedish math: no CAHLR repo found -> donor/recipients recorded only")

    # ── Validate every written value ──────────────────────────────────────────
    if problems:
        raise ValueError("Validation failed:\n  " + "\n  ".join(problems))
    n_written = sum(1 for r in rows if r["written"])
    print(f"\nValidation OK: all {n_written} written values in [0,1] and slip+guess < 1.")

    prov = pd.DataFrame(rows)
    print(f"Provenance rows: {len(prov)} "
          f"({n_written} written, {len(prov) - n_written} recorded-only)")
    print(f"Fill-source breakdown (written): "
          f"{dict(Counter(r['fill_source'] for r in rows if r['written']))}")

    # ── Write ─────────────────────────────────────────────────────────────────
    if args.dry_run:
        print("\n[dry-run] no files written.")
        return

    out_content = os.path.join(OUTPUT_DIR, "experimentalBKTParams.json")
    with open(out_content, "w") as f:
        json.dump(bkt, f, indent=4)
    print(f"\nWrote {out_content} ({len(bkt)} KCs, {n_content} updated)")

    for repo, repo_json in external_files.items():
        out = os.path.join(OUTPUT_DIR, f"{repo}BKTParams.json")
        with open(out, "w") as f:
            json.dump(repo_json, f, indent=4)
        print(f"Wrote {out} ({len(repo_json)} KCs)")

    prov.to_csv(os.path.normpath(PROVENANCE_CSV), index=False)
    print(f"Wrote {os.path.normpath(PROVENANCE_CSV)}")
    print("\ndefaultBKTParams.json untouched.")


if __name__ == "__main__":
    main()
