# BKT Parameter Fitting — Process Walkthrough

**Audience:** anyone re-running the fit with fresh data, adding a new content repo, or auditing why a KC has the params it has.

**Status (2026-07-12):** pipeline built and run once end-to-end; output computed but only partially merged into live content repos (§7).

This is the step-by-step to follow when re-running or extending the pipeline.

Each step ends with a one-line **Flexibility** tag; see §8 for the full table with reasoning.

---

## 0. Background

OATutor tracks mastery per knowledge component (KC) with 2-state BKT, 4 params each, stored in `bkt-params/experimentalBKTParams.json` per content repo:

| Field | pyBKT name | Meaning |
|---|---|---|
| `probMastery` | `prior` | P(already knows it before practice) |
| `probTransit` | `learns` | P(learns it on one attempt) |
| `probSlip` | `slips` | P(knows it, answers wrong) |
| `probGuess` | `guesses` | P(doesn't know it, answers right) |

Every KC ships with an untuned flat `0.1/0.1/0.1/0.1` default. This project fits real values from Firebase where there's enough data to trust the fit. `defaultBKTParams.json` is the untuned control and is **never edited** — only `experimentalBKTParams.json` is written, so tuned-vs-default stays A/B-comparable.

## 1. File map

```
bkt/pull_submissions.py       Firebase -> bkt/data/submissions.csv (gitignored)
bkt/fit_bkt.py                fit pyBKT; prototype JSON-write path (superseded by fill_disqualified_kc.py)
bkt/evaluate_bkt.ipynb        leave-last-out evaluation + tiering
bkt/fill_disqualified_kc.py   the real write pipeline: donors + domain-average recipient fill
bkt/output/                   committed JSON outputs
bkt/data/                     gitignored — regenerate locally before anything else works
```

## 2. Pull data

```bash
python bkt/pull_submissions.py
```
Streams all of Firestore's `problemSubmissions` (project `oatutor-askoski`, no semester filter) to `bkt/data/submissions.csv`. Needs Application Default Credentials with access to that project.

- Raw pull is unfiltered — event-type filtering happens downstream, not here.
- `knowledgeComponents` is a **stringified Python list** (`ast.literal_eval` + `.explode()` needed) — every consumer of this CSV does this; don't skip it in new code.

**Flexibility:** low — nothing to tune besides an unused `semester` filter arg.

## 3. Fit

```bash
python bkt/fit_bkt.py
```
- **Hint adjustment** (`HINT_ADJUSTED = True`, fixed): any answer preceded by a hint unlock for that step is marked incorrect before fitting — otherwise hint-assisted guesses inflate `probGuess`. Measured effect: median `probGuess` −0.165 across 97 KCs.
- **pyBKT EM bug (critical, silent):** `EM_fit.run()` gates its `Pool.map()` call behind `if __name__=="__main__"`, which is never true as a library import — the E-step never runs and M-step silently returns NaN prior / `learns=1.0, slips=0.5, guesses=0.5`, **no error thrown**. `_patch_pybkt()` fixes this by calling `inner()` directly; any new script calling `pyBKT.Model.fit()` must call it first. Sanity check: fitted `prior` should never be NaN, and params should never all sit exactly at `1.0/0.5/0.5`.
- **Version pin:** `pyBKT==1.4.1` (from GitHub, not the broken PyPI 1.4.2 wheel) + `scikit-learn<1.6`. 1.4.0 doesn't run on Python 3.12.
- **Filtering:** `MIN_STUDENTS=15`, `MIN_RESPONSES_PER_STUDENT=2` — qualifies 284/1,108 observed KCs. ⚠️ **`MIN_RESPONSES_PER_STUDENT` was never actually confirmed with Zach** (he said "2-3 depending on mastery threshold") — still open in every prior note. Confirm or compare against 3 before leaning on results.
- `fit_bkt.py`'s own JSON-write path has no quality gate and assumes a local `../../OATutor-Content` checkout — **use `fill_disqualified_kc.py` (§6) for a real params update**, not this script directly. It's kept because `evaluate_bkt.ipynb` imports its `_patch_pybkt()` / `hint_adjust_correct()` helpers.

**Flexibility:** patch/pins fixed (bug workarounds); hint adjustment fixed (data-integrity correction); filtering thresholds tunable heuristics, but `MIN_RESPONSES_PER_STUDENT` specifically is unresolved, not just flexible.

## 4. Evaluate & tier

`bkt/evaluate_bkt.ipynb`, over the 125 KCs that are both fitted and present in the JSON:

- **Leave-last-out:** hold out each student's last answer, predict it with a from-scratch BKT forward pass (independent of pyBKT), compare RMSE/AUC against the student's own history-average baseline (stronger than a flat-prior baseline).
- **Flags** (heuristic cutoffs): `probGuess>0.3`, `probSlip>0.3`, `probTransit>0.9` or `<0.02`, `probMastery>0.8`.
- **`cor85`/`cor95`:** consecutive corrects needed to cross 0.85/0.95 mastery, computed from the fitted params — catches broken mastery curves (e.g. `cor95=1`) that look fine param-by-param.
- **Tiers:** 1 Hard Disqualify / 2 Disqualify → **recipients**; 3 Keep w/ Notation / 4 Clean → **donors**. Last run: 89 donors, 36 recipients (28 writable; 8 in disconnected repos).
- Supersedes an earlier ad hoc flag-only pass (e.g. 3 KCs it called out as "degenerate slip=0/guess=0" already resolve correctly under this tiering) — don't re-run that older check separately.

**Flexibility:** flag cutoffs and tier/decision-rule numbers are tunable heuristics — retune with a stated reason if the KC mix changes materially; keep the two-part structure (param-sanity **and** predictive-fit-vs-baseline), collapsing to one alone was rejected.

## 5. Fill-strategy decision (disqualified KCs)

Answers the professor's question: domain average, global average, or something else, for recipients?

- **Domain = subject** (Algebra, Calc/PreCalc, Statistics, Physics, Other), built from `coursePlans.json`. Two coarser options were tested and rejected: by-organization (degenerates to global — all writable recipients are OpenStax), by-course (moves fills ~0.10 but for the wrong reason, and 16/28 recipients are multi-course so assignment is arbitrary).
- **Rule:** subject mean if that subject has ≥`MIN_DONORS`(5) donors (most-donor subject if multi-subject), else the global mean of all 89 donors (Algebra 47, Calc/PreCalc 40 qualify; Statistics 2, Physics 0 fall back).
- **Caveat to repeat if asked "how precise is this":** within-subject donor spread (std ≈0.18–0.22 on prior) *exceeds* the between-subject difference (~0.13) — this is a mildly better-targeted prior, not a precise correction.
- **Settled sub-decisions:** global fallback = all 89 donors (not an in-JSON-only 69); Tier 1 gets the same fill as Tier 2 (not a flat-0.1 revert); multi-subject → most-donor subject; all 36 recipients overwritten blanket, no reason-gating (every disqualification reason turned out to be parameter-driven, so nothing is trustworthy "for an unrelated reason").

**Flexibility:** `MIN_DONORS=5` tunable, but re-derive rather than assume if the donor distribution shifts (it currently sits exactly at the line separating qualifying/non-qualifying subjects). Subject-level granularity has empirical backing — don't revert casually. The settled sub-decisions had explicit sign-off; re-open only with similar sign-off.

## 6. Never-fitted KCs — leave at default

~836 of ~1,108 observed KCs never had enough data to fit and stay at flat `0.1/0.1/0.1/0.1`. **Do not fill these with a domain/global average** — unlike §5 recipients (which have a real, if untrustworthy, fit to fall back on), these have zero data to validate a fill against. This was explicitly considered ("Phase 2") and rejected as a default course of action.

**Flexibility:** none, by design. Filling these later is a new decision requiring its own sign-off, not a parameter change here.

## 7. Run the fill script

```bash
python bkt/fill_disqualified_kc.py --dry-run     # preview only
python bkt/fill_disqualified_kc.py               # writes bkt/output/*.json
```
Fetches `experimentalBKTParams.json` + `coursePlans.json` live from `CAHLR/OATutor-Content` (default ref `main`, no local checkout needed), applies §5's donor-fit/recipient-fill logic, writes `bkt/output/experimentalBKTParams.json` (1003 KCs, 105 updated) plus one file per external repo (Calbright, Chem1A/49/Chemistry), and a local provenance CSV (old → new value per KC, with fill source) as the audit trail. Validates every written value (`0≤x≤1`, `slip+guess<1`) before writing anything.

- 7 KCs got renamed upstream with an `_in_openstax_precalc` suffix — mapped via the `RENAMES` dict; watch the printed `Not in JSON` count if more renames happen upstream.
- 8/36 recipients aren't in the JSON at all (disconnected repos) — recorded for provenance only, expected not a bug.
- The `EXTERNAL_REPOS` dict is hand-maintained per fork — extend it, don't rewrite the fill logic, when adding a new repo.

**Flexibility:** mechanics are low-flexibility (faithful implementation of §5); the per-fork `EXTERNAL_REPOS` map needs updating whenever a repo's KC set changes.

## 8. Insert into content repos

Output JSON in `bkt/output/` doesn't take effect until committed into each repo's `bkt-params/experimentalBKTParams.json`.

- **Format already verified compatible** — same keys the app reads (`BKT-brain.js:13` reads `probTransit`; ignore the stale `probLearn` naming in `BKTPARAMS-EXPLAINED.md`).
- **`CAHLR/OATutor` main repo is dangerous to hand-edit:** its content-staging cron (twice daily) regenerates `defaultBKTParams.json` then blind-copies it to experimental. Fix: workflow calls `bkt/merge_experimental.py` (this repo) instead of `cp` — default's KC set wins, Tooling's fitted value wins per-KC where present, so experimental tracks content changes without losing tuning. Branch `experimental-bktparams-from-tooling` — **must merge after** the Tooling PR carrying `merge_experimental.py` + `bkt/output/experimentalBKTParams.json`.
- **Calbright and Chem1A forks are safe to hand-insert into** — same workflow file, but its cron has never actually fired on either (verify via `gh api repos/CAHLR/<repo>/actions/workflows/deploy-content-staging.yml/runs`, expect empty/404). Overwrite `experimentalBKTParams.json` wholesale with the matching `bkt/output/OATutor-<Fork>BKTParams.json`, leave `defaultBKTParams.json` alone, keep 4-space indent.
- **Chem49/Chemistry have output files but their fork-safety was never checked** — don't assume dormant crons without verifying the same way.
- **Fork-network gotcha:** every `CAHLR/OATutor*` content repo shares **one physical fork** per account (`mjyang00001/OATutor-CalbrightContent` is the canonical name for all of them). Same-name branches across "different" forks silently collide — use distinct branch names, and PR each branch against its correct CAHLR base repo. `OATutor-Tooling` and `OATutor-Content` are separate, real forks, not affected.

**Live status (2026-07-12, via `gh`):**

| Repo | Branch | PR |
|---|---|---|
| `OATutor-Tooling` | `feature/bkt-fitting` | [#16](https://github.com/CAHLR/OATutor-Tooling/pull/16) open |
| `OATutor-Tooling` | `deploy-experimental-bktparams` | [#15](https://github.com/CAHLR/OATutor-Tooling/pull/15) open |
| `OATutor` | `experimental-bktparams-from-tooling` | not yet opened |
| `OATutor-CalbrightContent` | `bkt-fitted-calbright` | not yet opened |
| `OATutor-Chem1A` | `bkt-fitted-chem1a` | not yet opened |
| `OATutor-Content` | `bkt-param-fill` | not yet opened |
| `OATutor-Chem49`, `OATutor-Chemistry` | — | not started |

(`OATutor` PR #105 "bktparams fix," open since 2026-03-06, predates this project and is unrelated.)

**Flexibility:** none on the ordering constraint or the "don't hand-edit main OATutor" rule — structural facts about the deploy workflow. Which of the pending branches gets a PR next is open.

---

## 9. Flexibility summary

| Decision | Flexibility |
|---|---|
| Hint adjustment, pyBKT patch, version pins | Fixed — bug workarounds / data-integrity corrections |
| `MIN_STUDENTS`, flag thresholds, tier/eval rules | Tunable heuristics — retune with a stated reason |
| `MIN_RESPONSES_PER_STUDENT` | Tunable, but **still unconfirmed with Zach** — resolve before relying on results |
| Subject-level domain granularity | Empirically backed — don't revert without redoing the comparison |
| `MIN_DONORS=5` | Tunable, re-derive if donor distribution shifts materially |
| Global-fallback/Tier-1-fill/multi-subject/blanket-overwrite sub-decisions | Settled, signed off — reopen only with similar sign-off |
| Never-fitted KCs stay at default | Fixed by design — no data to validate a fill |
| Main-OATutor deploy ordering, distinct fork branch names | Fixed — structural facts, not preferences |

## 10. Artifact index

- **Scripts:** `bkt/pull_submissions.py`, `fit_bkt.py`, `evaluate_bkt.ipynb`, `fill_disqualified_kc.py`, `explore_kcs.ipynb`
- **Data:** `bkt/data/fitted_params_hint_adjusted.csv` (gitignored, regenerate via §2–3) · `bkt/output/*.json` (deploy targets, §8). The KC classification (tiers, RMSE/AUC metrics) and per-recipient fill provenance referenced throughout are tracked internally, not in this repo's visible history.
