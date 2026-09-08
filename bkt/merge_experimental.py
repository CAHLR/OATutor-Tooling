"""
Merge this repo's fitted BKT params onto a freshly generated defaultBKTParams.json,
keyed by KC name, so experimentalBKTParams.json tracks default's live KC set
(new/removed/renamed KCs) while keeping tuned values where we have them.

Replaces a blind `cp defaultBKTParams.json experimentalBKTParams.json` in the
content-staging workflow: for each KC in the fresh default file, use the fitted
value from bkt/output/experimentalBKTParams.json if present, else fall back to
default's own (flat 0.1) value. KCs that exist in the fitted file but not in
default anymore (renamed/removed upstream) are dropped and logged, not carried
over -- default is the source of truth for which KCs exist.

Usage:
  python3 bkt/merge_experimental.py \
      --default path/to/defaultBKTParams.json \
      --fitted bkt/output/experimentalBKTParams.json \
      --out path/to/experimentalBKTParams.json
"""
import argparse
import json
import sys

PARAM_KEYS = ("probMastery", "probTransit", "probSlip", "probGuess")


def validate(kc, params):
    for k in PARAM_KEYS:
        v = params[k]
        if not (0 <= v <= 1):
            raise ValueError(f"{kc}.{k}={v} out of [0,1]")
    if params["probSlip"] + params["probGuess"] >= 1:
        raise ValueError(f"{kc}: probSlip ({params['probSlip']}) + "
                          f"probGuess ({params['probGuess']}) >= 1")


def merge(default, fitted):
    merged = {}
    used_fitted = 0
    for kc, params in default.items():
        source = fitted[kc] if kc in fitted else params
        merged[kc] = {k: source[k] for k in PARAM_KEYS}
        validate(kc, merged[kc])
        if kc in fitted:
            used_fitted += 1
    return merged, used_fitted


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--default", required=True, help="freshly generated defaultBKTParams.json")
    ap.add_argument("--fitted", required=True, help="this repo's committed bkt/output/experimentalBKTParams.json")
    ap.add_argument("--out", required=True, help="where to write the merged experimentalBKTParams.json")
    args = ap.parse_args()

    with open(args.default) as f:
        default = json.load(f)
    with open(args.fitted) as f:
        fitted = json.load(f)

    merged, used_fitted = merge(default, fitted)

    stale = sorted(set(fitted) - set(default))
    if stale:
        preview = stale[:10]
        suffix = "..." if len(stale) > 10 else ""
        print(f"[merge_experimental] {len(stale)} fitted KC(s) not in default, "
              f"dropped: {preview}{suffix}", file=sys.stderr)

    print(f"[merge_experimental] {used_fitted}/{len(default)} KCs used fitted "
          f"values, {len(default) - used_fitted} fell back to default.")

    with open(args.out, "w") as f:
        json.dump(merged, f, indent=4)


if __name__ == "__main__":
    main()
