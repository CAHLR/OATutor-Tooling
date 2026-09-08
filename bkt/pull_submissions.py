import os
import pandas as pd
from google.cloud import firestore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "submissions.csv")

PROJECT_ID = "oatutor-askoski"


def get_db():
    return firestore.Client(project=PROJECT_ID)


def pull_submissions(db, semester=None):
    """Pull problemSubmissions. Optionally filter to a specific semester string."""
    ref = db.collection("problemSubmissions")
    if semester:
        ref = ref.where("semester", "==", semester)
    docs = ref.stream()
    return pd.DataFrame(doc.to_dict() for doc in docs)


def main():
    print("Connecting to Firebase...")
    db = get_db()

    print("Pulling submissions (this may take a while)...")
    df = pull_submissions(db)
    print(f"  {len(df):,} rows pulled")
    print(f"  Columns: {list(df.columns)}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
