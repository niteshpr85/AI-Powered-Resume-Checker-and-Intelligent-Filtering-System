# AI-Powered Resume Checker and Intelligent Filtering System

Streamlit-based project that parses resumes, compares them with a Job Description (JD), computes ATS scores, filters candidates, and explains selection/rejection with actionable insights.

## Features

- Resume upload (`.pdf`, `.docx`) with automatic text extraction
- JD input (paste text or upload file)
- Stronger skill extraction and skill-gap detection
- Context-aware matching with TF-IDF cosine similarity
- ATS score with configurable weighted components
- Recruiter filtering (`min ATS`, `min experience`, `required skills`)
- Candidate ranking with decision explainability
- Resume quality analysis and improvement feedback
- Auto-generated interview questions
- Parsing warning when low text is extracted (common in scanned/image PDFs)
- Role-based authentication with login/register/logout (`admin` and `customer`)
- Advanced candidate search and view filters (status, shortlist-only, min probability)
- Analytics tab (status pie, ATS distribution, top skills)
- Comparison tab with side-by-side table and radar chart
- Saved Jobs manager (save/load/delete JD templates per user)
- Role Compare tab (score same candidate pool across multiple saved jobs)
- Admin panel for user management and global saved-job control
- Export both full results and filtered view CSV

## Project Structure

```text
resume_checker_ai/
|-- app.py
|-- requirements.txt
|-- README.md
|-- backend/
|   |-- __init__.py
|   |-- auth.py
|   |-- job_store.py
|   |-- parser.py
|   |-- jd_processor.py
|   |-- skill_extractor.py
|   |-- similarity_engine.py
|   |-- quality_analyzer.py
|   |-- scoring_engine.py
|   |-- filter_engine.py
|   |-- decision_explainer.py
|   `-- interview_generator.py
|-- utils/
|   |-- __init__.py
|   |-- constants.py
|   |-- helpers.py
|   `-- text_cleaner.py
|-- models/
|-- data/
`-- tests/
```

## Architecture

```text
Streamlit UI
   |
   v
Auth Layer (Login/Register)
   |
   v
Controller (app.py)
   |
   +--> Resume Parser
   +--> JD Processor
   +--> Skill Extractor + Similarity Engine
   +--> Scoring Engine
   +--> Filtering Engine
   +--> Decision Explainer + Interview Generator
   |
   v
Ranked Results + Insights Dashboard
```

## ATS Scoring Formula

Default weights:

- Skill Match: 30%
- Semantic Similarity: 25%
- Experience Match: 15%
- Education Match: 10%
- Resume Quality: 20%

`Final ATS = weighted sum of all component scores`

## Setup

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

## How to Use

1. Provide job description in sidebar (paste/upload).
2. Optionally save the JD in **Saved Jobs** for reuse.
3. Upload multiple resumes.
4. Adjust filters and score weights.
5. Click **Run Screening**.
6. Review `Candidates`, `Analytics`, and `Compare` tabs.
7. Use `Role Compare` tab to compare candidate fit across saved job roles.

## Admin vs Customer

- `Customer` account:
  - Full resume screening workflow
  - Saved Jobs (own account)
  - Candidate analytics, comparison, role comparison
- `Admin` account:
  - Admin control center
  - View all users
  - View all saved jobs across users
  - Delete any saved job

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

## Deploy (Streamlit Community Cloud)

1. Open https://share.streamlit.io
2. Login with GitHub and click **New app**
3. Select:
   - Repository: `<YOUR_USERNAME>/<YOUR_REPO>`
   - Branch: `main`
   - Main file path: `app.py`
4. Click **Deploy**

If build fails, check app logs and ensure `requirements.txt` installs correctly.

## Notes

- Parsing quality depends on resume formatting quality.
- Scanned/image PDFs often have very low extractable text without OCR.
- Current semantic engine uses TF-IDF for lightweight local execution.
- You can replace similarity layer with sentence-transformer embeddings later without changing UI flow.
