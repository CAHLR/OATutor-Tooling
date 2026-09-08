import ast
import json
import os
import numpy as np
import pandas as pd
from pyBKT.models import Model

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SUBMISSIONS_PATH = os.path.join(SCRIPT_DIR, "data", "submissions.csv")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "fitted_params.csv")
EXPERIMENTAL_PARAMS_PATH = os.path.join(SCRIPT_DIR, "../../OATutor-Content/bkt-params/experimentalBKTParams.json")

MIN_STUDENTS = 15
# 2-3 responses per student depending on mastery threshold; defaulting to 2
MIN_RESPONSES_PER_STUDENT = 2

# Set to True to mark hint-assisted answers as incorrect before fitting
HINT_ADJUSTED = True


def _patch_pybkt():
    """
    pyBKT bug: EM_fit.run() wraps Pool.map() in `if __name__ == "__main__"`,
    which is never True when called as a library. The E-step never runs,
    softcounts stay at zero, and the M-step returns NaN/default params.
    Fix: replace run() with an identical version that calls inner() directly.
    See: https://github.com/CAHLR/pyBKT/blob/master/pyBKT/fit/EM_fit.py
    """
    import pyBKT.fit.EM_fit as em
    from multiprocessing import cpu_count

    def _fixed_run(data, model, trans_softcounts, emission_softcounts,
                   init_softcounts, num_outputs, parallel=True, fixed={}):
        alldata = data["data"]
        bigT, num_subparts = len(alldata[0]), len(alldata)
        allresources, starts, learns, forgets, guesses, slips, lengths = \
            data["resources"], data["starts"], model["learns"], model["forgets"], \
            model["guesses"], model["slips"], data["lengths"]
        prior, num_sequences, num_resources = model["prior"], len(starts), len(learns)
        normalizeLengths = False

        if 'prior' in fixed:
            prior = fixed['prior']
        initial_distn = np.empty((2,), dtype='float')
        initial_distn[0] = 1 - prior
        initial_distn[1] = prior

        if 'learns' in fixed:
            learns = learns * (fixed['learns'] < 0) + fixed['learns'] * (fixed['learns'] >= 0)
        if 'forgets' in fixed:
            forgets = forgets * (fixed['forgets'] < 0) + fixed['forgets'] * (fixed['forgets'] >= 0)
        As = np.empty((2, 2 * num_resources))
        em.interleave(As[0], 1 - learns, forgets.copy())
        em.interleave(As[1], learns.copy(), 1 - forgets)

        if 'guesses' in fixed:
            guesses = fixed['guesses'] * (fixed['guesses'] < 0) + fixed['guesses'] * (fixed['guesses'] >= 0)
        if 'slips' in fixed:
            slips = fixed['slips'] * (fixed['slips'] < 0) + fixed['slips'] * (fixed['slips'] >= 0)
        Bn = np.empty((2, 2 * num_subparts))
        em.interleave(Bn[0], 1 - guesses, guesses.copy())
        em.interleave(Bn[1], slips.copy(), 1 - slips)

        all_trans_softcounts = np.zeros((2, 2 * num_resources))
        all_emission_softcounts = np.zeros((2, 2 * num_subparts))
        all_initial_softcounts = np.zeros((2, 1))
        alpha_out = np.zeros((2, bigT))
        total_loglike = np.empty((1, 1))
        total_loglike.fill(0)

        input_data = {
            "As": As, "Bn": Bn, "initial_distn": initial_distn,
            "allresources": allresources, "starts": starts, "lengths": lengths,
            "num_resources": num_resources, "num_subparts": num_subparts,
            "alldata": alldata, "normalizeLengths": normalizeLengths, "alpha_out": alpha_out,
        }

        num_threads = cpu_count() if parallel else 1
        thread_counts = []
        for thread_num in range(num_threads):
            blocklen = 1 + ((num_sequences - 1) // num_threads)
            seq_start = int(blocklen * thread_num)
            seq_end = min(seq_start + blocklen, num_sequences)
            tc = {"sequence_idx_start": seq_start, "sequence_idx_end": seq_end}
            tc.update(input_data)
            thread_counts.append(tc)

        x = [em.inner(tc) for tc in thread_counts]

        for i in x:
            total_loglike += i[3]
            all_trans_softcounts += i[0]
            all_emission_softcounts += i[1]
            all_initial_softcounts += i[2]
            for seq_start, T, alpha in i[4]:
                alpha_out[:, seq_start:seq_start + T] += alpha

        all_trans_softcounts = all_trans_softcounts.flatten(order='F')
        all_emission_softcounts = all_emission_softcounts.flatten(order='F')
        return {
            "total_loglike": total_loglike,
            "all_trans_softcounts": np.reshape(all_trans_softcounts, (num_resources, 2, 2), order='C'),
            "all_emission_softcounts": np.reshape(all_emission_softcounts, (num_subparts, 2, 2), order='C'),
            "all_initial_softcounts": all_initial_softcounts,
            "alpha_out": alpha_out.flatten(order='F').reshape(alpha_out.shape, order='C'),
        }

    em.run = _fixed_run


def hint_adjust_correct(df_raw):
    """Mark any answerStep as incorrect if the student unlocked a hint for that
    (user, stepID) before that specific answer timestamp."""
    hints = df_raw[df_raw["eventType"] == "unlockHint"][["oats_user_id", "stepID", "time_stamp"]].copy()
    hints = hints.rename(columns={"oats_user_id": "user_id", "time_stamp": "hint_time"})

    answers = df_raw[df_raw["eventType"] == "answerStep"].copy()
    answers = answers.rename(columns={"oats_user_id": "user_id", "time_stamp": "ans_time"})

    # Join answers with hints on (user, stepID), keep only hints before the answer
    merged = answers.merge(hints, on=["user_id", "stepID"], how="left")
    hint_assisted = (
        merged[merged["hint_time"] < merged["ans_time"]][["user_id", "stepID", "ans_time"]]
        .drop_duplicates()
        .assign(hint_assisted=True)
    )

    answers = answers.merge(hint_assisted, on=["user_id", "stepID", "ans_time"], how="left")
    n_adjusted = answers["hint_assisted"].notna().sum()
    print(f"  {n_adjusted:,} answers marked incorrect due to prior hint use")

    answers.loc[answers["hint_assisted"].notna(), "isCorrect"] = False
    return answers.drop(columns=["hint_assisted"]).rename(columns={"ans_time": "time_stamp"})


def load_and_prepare(path, hint_adjusted=False):
    df_raw = pd.read_csv(path, low_memory=False)

    if hint_adjusted:
        print("Applying hint adjustment...")
        df = hint_adjust_correct(df_raw)
    else:
        df = df_raw[df_raw["eventType"] == "answerStep"].copy()

    df = df[df["knowledgeComponents"].notna()]
    df["knowledgeComponents"] = df["knowledgeComponents"].apply(ast.literal_eval)
    df = df.explode("knowledgeComponents")

    df = df.rename(columns={
        "oats_user_id": "user_id",   
        "knowledgeComponents": "skill_name",
        "time_stamp": "order_id",
        "isCorrect": "correct",
    })

    df["correct"] = df["correct"].astype(int)
    df = df[["user_id", "skill_name", "order_id", "correct"]].dropna()

    return df


def filter_sufficient_kcs(df):
    response_counts = df.groupby(["skill_name", "user_id"]).size()
    qualified = response_counts[response_counts >= MIN_RESPONSES_PER_STUDENT].reset_index()[["skill_name", "user_id"]]
    df = df.merge(qualified, on=["skill_name", "user_id"], how="inner")

    student_counts = df.groupby("skill_name")["user_id"].nunique()
    valid = student_counts[student_counts >= MIN_STUDENTS].index
    print(f"  {len(valid)} KCs with >= {MIN_STUDENTS} students each having >= {MIN_RESPONSES_PER_STUDENT} responses (out of {df['skill_name'].nunique()} total)")
    return df[df["skill_name"].isin(valid)]


PYBKT_TO_JSON = {
    "prior":   "probMastery",
    "learns":  "probTransit",
    "slips":   "probSlip",
    "guesses": "probGuess",
}


def update_experimental_params(params):
    path = os.path.normpath(EXPERIMENTAL_PARAMS_PATH)
    with open(path) as f:
        bkt_params = json.load(f)

    flat = params["value"].unstack("param").droplevel("class")

    updated, skipped_nan, skipped_missing = 0, 0, 0
    for kc, row in flat.iterrows():
        if row[list(PYBKT_TO_JSON.keys())].isna().any():
            skipped_nan += 1
            continue
        if kc not in bkt_params:
            skipped_missing += 1
            continue
        for pybkt_col, json_field in PYBKT_TO_JSON.items():
            bkt_params[kc][json_field] = round(float(row[pybkt_col]), 6)
        updated += 1

    print(f"  Updated: {updated} | Skipped (NaN params): {skipped_nan} | Not in JSON: {skipped_missing}")

    with open(path, "w") as f:
        json.dump(bkt_params, f, indent=4)   # match the committed file's 4-space indent
    print(f"  Written to {path}")


def main():
    _patch_pybkt()

    suffix = "_hint_adjusted" if HINT_ADJUSTED else ""
    output_path = OUTPUT_PATH.replace(".csv", f"{suffix}.csv")

    print("Loading submissions...")
    df = load_and_prepare(SUBMISSIONS_PATH, hint_adjusted=HINT_ADJUSTED)
    print(f"  {len(df):,} answerStep rows")

    print("Filtering KCs by student count...")
    df = filter_sufficient_kcs(df)
    print(f"  {len(df):,} rows remaining")

    print("Fitting pyBKT model (this may take a while)...")
    model = Model(seed=42)
    model.fit(data=df)
    params = model.params()

    n_kcs = params.index.get_level_values("skill").nunique()
    print(f"\nFitted {n_kcs} KCs")
    params.to_csv(output_path)
    print(f"Saved to {output_path}")

    print("\nUpdating experimentalBKTParams.json...")
    update_experimental_params(params)


if __name__ == "__main__":
    main()
