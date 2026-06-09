"""
main.py — AI Job Scorer
=======================
Reads jobs.csv → scores each job using Claude Haiku → saves to scored_jobs.csv

USAGE:
------
    python main.py

REQUIREMENTS:
-------------
    pip install pandas anthropic

OUTPUT:
-------
    scored_jobs.csv — with AI score, verdict, skills match, ATS keywords
"""

import pandas as pd
from ai_scorer import score_job

# ── Config ────────────────────────────────────────────────────────────────────

INPUT_FILE  = "jobs.csv"
OUTPUT_FILE = "scored_jobs.csv"
TEST_LIMIT  = 10   # Process only first N jobs (set to None for all jobs)

# ── Helpers ───────────────────────────────────────────────────────────────────

def flatten_list(value) -> str:
    """Convert a list to comma-separated string for CSV storage."""
    if isinstance(value, list):
        return ", ".join(value)
    return str(value) if value else ""


def load_jobs(filepath: str) -> pd.DataFrame:
    """Load jobs.csv and validate required columns exist."""
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        print("   Run scraper.py first to generate jobs.csv")
        raise SystemExit(1)

    required_columns = {"title", "company", "description"}
    missing = required_columns - set(df.columns)
    if missing:
        print(f"❌ jobs.csv is missing columns: {missing}")
        raise SystemExit(1)

    # Fill missing values so scorer doesn't receive NaN
    df["title"]       = df["title"].fillna("Unknown Title")
    df["company"]     = df["company"].fillna("Unknown Company")
    df["description"] = df["description"].fillna("")

    return df


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AI Job Scorer — Starting")
    print(f"  Input  : {INPUT_FILE}")
    print(f"  Output : {OUTPUT_FILE}")
    print(f"  Model  : claude-haiku-4-5-20251001")
    print("=" * 60)

    # Load jobs
    df = load_jobs(INPUT_FILE)
    total_available = len(df)

    # Apply test limit
    if TEST_LIMIT:
        df = df.head(TEST_LIMIT)

    total = len(df)
    print(f"\n  Total jobs in CSV  : {total_available}")
    print(f"  Jobs to score now  : {total}")
    print()

    results = []
    success_count = 0
    error_count   = 0

    for idx, row in df.iterrows():
        job_num  = idx + 1
        title    = row["title"]
        company  = row["company"]
        desc     = row["description"]

        print(f"  [{job_num}/{total}] Scoring: {title} @ {company}")

        # ── Call AI scorer ────────────────────────────────────────────────
        try:
            result = score_job(
                job_title=title,
                company=company,
                job_description=desc,
            )

            # Validate score exists
            score = result.get("score", 0)
            if not isinstance(score, (int, float)):
                score = 0

            results.append({
                "title":          title,
                "company":        company,
                "score":          score,
                "verdict":        result.get("verdict", ""),
                "matching_skills": flatten_list(result.get("matching_skills", [])),
                "missing_skills":  flatten_list(result.get("missing_skills", [])),
                "ats_keywords":    flatten_list(result.get("ats_keywords", [])),
                "resume_tweaks":   result.get("resume_tweaks", ""),
            })

            # Show quick inline result
            score_display = f"{score}/10"
            verdict_short = result.get("verdict", "")[:60]
            flag = "✅" if score >= 7 else "⚠️ " if score >= 5 else "❌"
            print(f"         {flag} Score: {score_display} — {verdict_short}")
            success_count += 1

        except Exception as e:
            # Graceful error handling — log and continue
            print(f"         ⚠ API error for job [{job_num}]: {e}")
            results.append({
                "title":           title,
                "company":         company,
                "score":           0,
                "verdict":         f"Error: {str(e)[:100]}",
                "matching_skills": "",
                "missing_skills":  "",
                "ats_keywords":    "",
                "resume_tweaks":   "",
            })
            error_count += 1

        print()  # blank line between jobs for readability

    # ── Save results ──────────────────────────────────────────────────────────
    results_df = pd.DataFrame(results)

    # Sort by score descending so best matches appear first
    results_df = results_df.sort_values("score", ascending=False).reset_index(drop=True)

    results_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 60)
    print(f"  ✅ Scoring complete!")
    print(f"  Successful : {success_count}/{total}")
    print(f"  Errors     : {error_count}/{total}")
    print(f"  Output     : {OUTPUT_FILE}")
    print()

    if success_count > 0:
        top = results_df[results_df["score"] >= 7]
        mid = results_df[(results_df["score"] >= 5) & (results_df["score"] < 7)]
        low = results_df[results_df["score"] < 5]
        print(f"  ✅ Apply now  (score ≥ 7) : {len(top)} jobs")
        print(f"  ⚠️  Consider  (score 5-6) : {len(mid)} jobs")
        print(f"  ❌ Skip       (score < 5) : {len(low)} jobs")
        print()
        if len(top) > 0:
            print("  Top matches:")
            for _, r in top.head(5).iterrows():
                print(f"    • {r['title']} @ {r['company']} — {r['score']}/10")

    print("=" * 60)


if __name__ == "__main__":
    main()
