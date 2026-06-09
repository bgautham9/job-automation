"""
ai_scorer.py — Uses Claude Haiku to score job fit and generate cover letters.
Cost: ~₹0.10 per job scored. Set ANTHROPIC_API_KEY in config.py
"""

import anthropic
import json
import re
from config import ANTHROPIC_API_KEY, RESUME_TEXT

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def score_job(job_title: str, company: str, job_description: str) -> dict:
    """
    Score a job against Gowtham's resume.
    Returns: { score, verdict, matching_skills, missing_skills, ats_keywords, resume_tweaks }
    """
    prompt = f"""You are a job fit analyzer. Analyze the match between this resume and job.

RESUME:
{RESUME_TEXT}

JOB TITLE: {job_title}
COMPANY: {company}
JOB DESCRIPTION:
{job_description[:3000]}

Respond ONLY in this exact JSON format (no markdown, no backticks, no extra text):
{{
  "score": <integer 1-10>,
  "verdict": "<one sentence — Apply / Consider / Skip and why>",
  "matching_skills": ["skill1", "skill2", "skill3"],
  "missing_skills": ["skill1", "skill2"],
  "ats_keywords": ["kw1", "kw2", "kw3", "kw4", "kw5"],
  "resume_tweaks": "<one sentence on what to highlight for this specific role>"
}}"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip any accidental markdown
        raw = re.sub(r'```json|```', '', raw).strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  [AI Scorer] Error: {e}")
        return {
            "score": 0, "verdict": "Error scoring",
            "matching_skills": [], "missing_skills": [],
            "ats_keywords": [], "resume_tweaks": ""
        }


def generate_cover_letter(job_title: str, company: str, job_description: str) -> str:
    """
    Generate a tailored 150-word cover letter for a specific job.
    Only call this for jobs scoring >= AUTO_APPLY_THRESHOLD to save cost.
    """
    prompt = f"""Write a short, professional cover letter (under 150 words) for this candidate.

CANDIDATE: B. Gowtham Kumar Reddy, Senior Data Analyst, Hyderabad
RESUME SUMMARY: {RESUME_TEXT[:800]}

APPLYING FOR: {job_title} at {company}
JOB DESCRIPTION (key parts): {job_description[:1500]}

Instructions:
- Start directly with a strong opening line (no "Dear Hiring Manager" needed)
- Mention 2-3 specific skills that match the JD
- Reference one real achievement from the resume
- End with a clear call to action
- Keep it under 150 words
- Do NOT invent fake achievements"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"  [Cover Letter] Error: {e}")
        return ""


if __name__ == "__main__":
    # Quick test
    print("Testing AI scorer...")
    result = score_job(
        "Senior Data Analyst",
        "Test Company",
        "We need a Power BI expert with 5+ years experience in DAX, SQL, and data modeling. Experience with ETL pipelines required."
    )
    print(f"Score: {result['score']}/10")
    print(f"Verdict: {result['verdict']}")
    print(f"Matching: {result['matching_skills']}")