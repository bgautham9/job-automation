# ============================================================
#  JOB AUTOMATION CONFIG — Edit this file before running
# ============================================================

# --- YOUR CREDENTIALS ---
NAUKRI_EMAIL    = "your_naukri_email@gmail.com"
NAUKRI_PASSWORD = "your_naukri_password"

LINKEDIN_EMAIL    = "your_linkedin_email@gmail.com"
LINKEDIN_PASSWORD = "your_linkedin_password"

INDEED_EMAIL    = "your_indeed_email@gmail.com"
INDEED_PASSWORD = "your_indeed_password"

# --- CLAUDE API KEY ---
# Get from: https://console.anthropic.com → API Keys → Create Key
ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxxxxxxxxx"

# --- JOB SEARCH PREFERENCES ---
JOB_KEYWORDS = [
    "Senior Data Analyst",
    "BI Developer",
    "Power BI Developer",
    "Business Intelligence Analyst",
    "Data Analyst Power BI",
]

LOCATIONS = ["Hyderabad", "Bengaluru", "Remote"]

EXPERIENCE_MIN = 5   # years
EXPERIENCE_MAX = 9   # years

SALARY_MIN_LPA = 12  # lakhs per annum (for Naukri filter)

# --- AI SCORING THRESHOLD ---
# Jobs scoring >= this will be auto-applied. Below = saved for manual review.
AUTO_APPLY_THRESHOLD = 7

# --- HOW MANY JOBS TO PROCESS PER RUN ---
MAX_JOBS_PER_PORTAL = 20  # per keyword per portal

# --- YOUR RESUME TEXT (used for AI scoring) ---
RESUME_TEXT = """
B. Gowtham Kumar Reddy — Senior Data Analyst & BI Developer, 6+ years experience.
Location: Hyderabad, India.

Skills: Power BI (DAX, Power Query, RLS, Workspaces), SQL (CTEs, Joins, Window Functions),
Python (Pandas, NumPy), Looker Studio, Microsoft SQL Server, DBeaver,
Star/Snowflake Schema, KPI Design, Trend Analysis, ETL, Data Pipelines,
API Integration, Agile, UAT, Stakeholder Communication, Executive Reporting, Team Mentorship.

Experience:
- Thryve Digital (Jul 2022 – Sep 2025): Senior Analyst/BI Developer.
  Built PLX and Looker dashboards, Power BI dashboards with DAX/RLS,
  optimized data models improving performance by 35%, reduced ad-hoc reporting by 25%,
  mentored junior analysts, end-to-end BI delivery.

- EDGEROCK SOFTWARE (Dec 2020 – Jul 2022): Data Analyst.
  BI dashboards, DAX, data transformation, 15% improvement in resolution efficiency.

- EDGEROCK SOFTWARE (Jan 2019 – Nov 2020): API Developer.
  Axway/Stoplight integrations, Python/SQL data transformation.

Key Projects:
- Performance Dashboard & Incident Analytics: reduced issue recurrence by 18%
- Data Migration & Validation Suite: 99.5% data integrity post-migration
- Customer Feedback & Insight Dashboard: 10% increase in satisfaction

Education:
- PGDM Supply Chain & Operations, ITM Business School, 2015
- BE Electronics & Communication, JNTU Hyderabad, 2012
"""

# --- COVER LETTER TEMPLATE (AI will customize per job) ---
COVER_LETTER_INTRO = "B. Gowtham Kumar Reddy, Senior Data Analyst with 6+ years in Power BI, SQL, and BI development based in Hyderabad."