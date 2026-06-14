"""Refit BKT for a single KC that has a typo variant, merging both into one."""
import ast, json, os
import numpy as np
import pandas as pd
from pyBKT.models import Model
from fit_bkt import _patch_pybkt, hint_adjust_correct

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SUBMISSIONS_PATH = os.path.join(SCRIPT_DIR, "data", "submissions.csv")
PARAMS_PATH = os.path.join(SCRIPT_DIR, "data", "fitted_params_hint_adjusted.csv")

# ── Config ────────────────────────────────────────────────────────────────────
CANONICAL  = "professional_learning"   # name to keep
TYPO       = "proffesional_learning"   # name to merge in
HINT_ADJUSTED = True
# ─────────────────────────────────────────────────────────────────────────────


def main():
    _patch_pybkt()

    df_raw = pd.read_csv(SUBMISSIONS_PATH, low_memory=False)

    if HINT_ADJUSTED:
        df = hint_adjust_correct(df_raw)
    else:
        df = df_raw[df_raw["eventType"] == "answerStep"].copy()

    df = df[df["knowledgeComponents"].notna()]
    df["knowledgeComponents"] = df["knowledgeComponents"].apply(ast.literal_eval)
    df = df.explode("knowledgeComponents")

    # Merge typo into canonical
    df["knowledgeComponents"] = df["knowledgeComponents"].replace(TYPO, CANONICAL)

    df = df[df["knowledgeComponents"] == CANONICAL].rename(columns={
        "oats_user_id":        "user_id",
        "knowledgeComponents": "skill_name",
        "time_stamp":          "order_id",
        "isCorrect":           "correct",
    })
    df["correct"] = df["correct"].astype(int)
    df = df[["user_id", "skill_name", "order_id", "correct"]].dropna()

    print(f"Fitting '{CANONICAL}' (merged with '{TYPO}')")
    print(f"  {df['user_id'].nunique()} students, {len(df)} responses")

    model = Model(seed=42)
    model.fit(data=df)
    new_params = model.params()
    print("\nNew params:")
    print(new_params)

    # Update fitted_params_hint_adjusted.csv
    existing = pd.read_csv(PARAMS_PATH, index_col=[0, 1, 2])
    # Drop old rows for both canonical and typo
    drop_mask = existing.index.get_level_values(0).isin([CANONICAL, TYPO])
    existing = existing[~drop_mask]
    updated = pd.concat([existing, new_params])
    updated.to_csv(PARAMS_PATH)
    print(f"\nUpdated {PARAMS_PATH}")
    print(f"  Removed '{TYPO}' row, replaced '{CANONICAL}' with merged fit.")


if __name__ == "__main__":
    main()
