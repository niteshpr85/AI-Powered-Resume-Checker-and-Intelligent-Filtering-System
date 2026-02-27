from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.auth import init_auth_db, list_users, login_user, register_user
from backend.decision_explainer import explain_decision
from backend.filter_engine import filter_candidates
from backend.interview_generator import generate_interview_questions
from backend.jd_processor import process_jd
from backend.job_store import (
    create_saved_job,
    delete_saved_job,
    delete_saved_job_admin,
    get_saved_job,
    init_job_db,
    list_all_saved_jobs,
    list_saved_jobs,
)
from backend.parser import parse_resume_file
from backend.scoring_engine import score_candidate
from utils.constants import DEFAULT_WEIGHTS, SKILL_CATALOG
from utils.helpers import normalize_weights


def _inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@400;600;700&display=swap');

        .stApp {
            background:
              radial-gradient(1200px 500px at 10% -20%, rgba(0, 147, 121, 0.15), transparent 60%),
              radial-gradient(900px 450px at 95% 5%, rgba(239, 108, 0, 0.12), transparent 55%),
              linear-gradient(160deg, #f4f8fa 0%, #fbf7f2 100%);
            color: #11253b;
            font-family: "Manrope", sans-serif;
        }

        h1, h2, h3 {
            font-family: "Space Grotesk", sans-serif !important;
            color: #0f2f4f;
            letter-spacing: -0.01em;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #133a5a 0%, #0f2f4f 100%);
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] small,
        [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
            color: #f2f7fb !important;
        }
        [data-testid="stSidebar"] .stMarkdown span,
        [data-testid="stSidebar"] .stMarkdown p {
            color: #f2f7fb !important;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea {
            color: #0f2f4f !important;
            background: #ffffff !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            color: #0f2f4f !important;
            background: #ffffff !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="select"] input {
            color: #102a43 !important;
            -webkit-text-fill-color: #102a43 !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="tag"] {
            background: #eaf2ff !important;
            border-color: #c4d7f2 !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="tag"] span,
        [data-testid="stSidebar"] div[data-baseweb="tag"] svg {
            color: #143556 !important;
            fill: #143556 !important;
        }
        [data-testid="stSidebar"] [data-baseweb="slider"] span {
            color: #f2f7fb !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            color: #0f2f4f !important;
            background: #ffd166 !important;
            border: 1px solid #f4b637 !important;
            font-weight: 700 !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: #ffca4f !important;
            color: #0b2239 !important;
        }

        [data-testid="stMainBlockContainer"],
        [data-testid="stMainBlockContainer"] p,
        [data-testid="stMainBlockContainer"] label,
        [data-testid="stMainBlockContainer"] span,
        [data-testid="stMainBlockContainer"] small {
            color: #102a43;
        }
        [data-testid="stMainBlockContainer"] input,
        [data-testid="stMainBlockContainer"] textarea {
            color: #102a43 !important;
            background: #ffffff !important;
        }
        [data-testid="stMainBlockContainer"] div[data-baseweb="select"] > div {
            color: #102a43 !important;
            background: #ffffff !important;
        }
        [data-testid="stMainBlockContainer"] div[data-baseweb="select"] input {
            color: #102a43 !important;
            -webkit-text-fill-color: #102a43 !important;
        }
        [data-testid="stMainBlockContainer"] div[data-baseweb="tag"] span {
            color: #143556 !important;
        }
        div[data-baseweb="tab-list"] button {
            color: #17324d !important;
            background: #eaf1f7 !important;
            border-radius: 10px !important;
        }
        div[data-baseweb="tab-list"] button[aria-selected="true"] {
            color: #ffffff !important;
            background: #133a5a !important;
        }

        div[data-baseweb="menu"] *,
        div[data-baseweb="popover"] * {
            color: #102a43 !important;
        }
        div[data-baseweb="menu"] {
            background: #ffffff !important;
        }

        [data-testid="stAlert"] p,
        [data-testid="stAlert"] div {
            color: #102a43 !important;
        }
        [data-testid="stDataFrame"] *,
        [data-testid="stDataEditor"] *,
        [data-testid="stTable"] * {
            color: #102a43 !important;
        }
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] p,
        [data-testid="stExpander"] span,
        [data-testid="stExpander"] div {
            color: #102a43 !important;
        }

        .hero-card {
            background: linear-gradient(130deg, rgba(19,58,90,0.94) 0%, rgba(0,147,121,0.82) 100%);
            border-radius: 18px;
            padding: 20px 24px;
            border: 1px solid rgba(255,255,255,0.16);
            box-shadow: 0 12px 30px rgba(13,42,70,0.16);
            margin-bottom: 14px;
        }
        .hero-card h2 {
            color: #f2fbff !important;
            margin: 0 0 6px 0;
        }
        .hero-card p {
            color: #e6f3f7;
            margin: 0;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #dce7f0;
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 6px 14px rgba(17,37,59,0.06);
            min-height: 102px;
        }
        .metric-label {
            font-size: 12px;
            color: #47627f;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .metric-value {
            font-size: 30px;
            font-weight: 700;
            color: #133a5a;
            line-height: 1.2;
        }
        .metric-accent {
            height: 6px;
            border-radius: 20px;
            margin-top: 10px;
            background: linear-gradient(90deg, #2f80ed 0%, #56ccf2 100%);
        }
        .page-head {
            text-align: center;
            margin-bottom: 6px;
        }
        .page-head h1 {
            margin-bottom: 4px;
        }
        .page-head p {
            color: #37526d;
            margin-top: 0;
        }
        .sidebar-nav {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.13);
            border-radius: 12px;
            padding: 10px 12px;
            margin: 8px 0 14px 0;
        }
        .sidebar-nav .item {
            padding: 7px 6px;
            border-radius: 8px;
            color: #eaf2fb !important;
            font-size: 15px;
        }
        .sidebar-nav .item.active {
            background: rgba(47, 128, 237, 0.28);
            font-weight: 700;
        }
        .badge {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid #dbe7f5;
            margin: 3px 4px 3px 0;
            font-size: 13px;
            font-weight: 600;
            background: #f5f9ff;
            color: #21405f !important;
        }
        .badge-red {
            background: #fff2f2;
            border-color: #ffd5d5;
            color: #c0392b !important;
        }
        .badge-green {
            background: #ecfbf1;
            border-color: #cdeed7;
            color: #1f7a3f !important;
        }
        .feedback-box {
            background: #ffffff;
            border: 1px solid #dce7f0;
            border-radius: 14px;
            padding: 14px;
        }

        .auth-box {
            background: #ffffff;
            border: 1px solid #dce7f0;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 22px rgba(17,37,59,0.08);
        }

        .panel-card {
            background: #ffffff;
            border: 1px solid #dce7f0;
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 6px 14px rgba(17,37,59,0.06);
            margin-bottom: 12px;
        }
        [data-testid="stSidebar"] .panel-card,
        [data-testid="stSidebar"] .panel-card p,
        [data-testid="stSidebar"] .panel-card b,
        [data-testid="stSidebar"] .panel-card .metric-label {
            color: #102a43 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _read_jd_text(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix in {".pdf", ".docx"}:
        return str(parse_resume_file(uploaded_file).get("raw_text", ""))
    return uploaded_file.getvalue().decode("utf-8", errors="ignore")


def _build_weights(slider_values: Dict[str, int]) -> Dict[str, float]:
    raw = {k: v / 100.0 for k, v in slider_values.items()}
    return normalize_weights(raw)


def _init_state() -> None:
    st.session_state.setdefault("screened_rows", [])
    st.session_state.setdefault("parsed_candidates", [])
    st.session_state.setdefault("jd_data", {})
    st.session_state.setdefault("selected_name", "")
    st.session_state.setdefault("auth_user", None)
    st.session_state.setdefault("auth_role", None)
    st.session_state.setdefault("jd_mode", "Paste Text")
    st.session_state.setdefault("jd_text_area", "")
    st.session_state.setdefault("last_weights", DEFAULT_WEIGHTS.copy())
    st.session_state.setdefault("last_min_score", 70)
    st.session_state.setdefault("last_min_experience", 1)


def _render_auth_screen() -> None:
    st.markdown(
        """
        <div class="hero-card">
          <h2>Resume Intelligence Portal</h2>
          <p>Secure login required before screening and ranking candidates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.3, 1])
    del left, right

    with center:
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                success, message = login_user(username=username, password=password)
                if success:
                    if isinstance(message, dict):
                        st.session_state["auth_user"] = message.get("username")
                        st.session_state["auth_role"] = message.get("role", "customer")
                    else:
                        st.session_state["auth_user"] = str(message)
                        st.session_state["auth_role"] = "customer"
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error(message)

        with register_tab:
            with st.form("register_form"):
                username = st.text_input("Create Username", key="register_username")
                email = st.text_input("Email", key="register_email")
                role = st.selectbox("Account Type", ["customer", "admin"], format_func=lambda x: x.title())
                password = st.text_input("Create Password", type="password", key="register_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
                submitted = st.form_submit_button("Register", use_container_width=True)
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register_user(username=username, email=email, password=password, role=role)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        st.markdown("</div>", unsafe_allow_html=True)


def _render_metric_cards(total: int, shortlisted: int, avg_score: float, avg_probability: float) -> None:
    col1, col2, col3, col4 = st.columns(4)
    cards = [
        ("Total Resumes", str(total), "#2f80ed"),
        ("Average ATS", f"{avg_score:.1f}%", "#27ae60"),
        ("Shortlisted", str(shortlisted), "#27ae60"),
        ("Selection Probability", f"{avg_probability:.0f}%", "#9b51e0"),
    ]
    for col, (label, value, color) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-accent" style="background:{color};"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_admin_metric_cards(total_users: int, admin_users: int, saved_jobs: int, customer_users: int) -> None:
    col1, col2, col3, col4 = st.columns(4)
    cards = [
        ("Total Users", str(total_users), "#2f80ed"),
        ("Admin Users", str(admin_users), "#9b51e0"),
        ("Saved Jobs", str(saved_jobs), "#27ae60"),
        ("Customer Users", str(customer_users), "#f2994a"),
    ]
    for col, (label, value, color) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-accent" style="background:{color};"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _list_to_text(values: object) -> str:
    if isinstance(values, list):
        return ", ".join(str(v) for v in values) if values else "None"
    return "None"


def _filter_candidates_view(df: pd.DataFrame) -> pd.DataFrame:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
    with col1:
        query = st.text_input("Search candidate/skill", placeholder="Name or skill keyword")
    with col2:
        status_options = ["All", "Shortlisted", "Rejected"]
        status_filter = st.selectbox("Status", status_options)
    with col3:
        min_probability = st.slider("Min Probability", 0, 100, 0)
    with col4:
        shortlist_only = st.checkbox("Shortlisted only", value=False)

    filtered = df.copy()
    if query.strip():
        q = query.strip().lower()
        filtered = filtered[
            filtered["name"].astype(str).str.lower().str.contains(q)
            | filtered["skills"].astype(str).str.lower().str.contains(q)
            | filtered["missing_skills"].astype(str).str.lower().str.contains(q)
        ]
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]
    if shortlist_only:
        filtered = filtered[filtered["status"] == "Shortlisted"]
    filtered = filtered[filtered["selection_probability"] >= min_probability]

    st.markdown("</div>", unsafe_allow_html=True)
    return filtered


def _render_analytics_tab(df: pd.DataFrame) -> None:
    st.markdown("### Analytics")
    col1, col2 = st.columns(2)

    with col1:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_status = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.45,
            color="Status",
            color_discrete_map={"Shortlisted": "#0f8a6f", "Rejected": "#ef6c00"},
            title="Shortlist vs Rejected",
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        fig_hist = px.histogram(
            df,
            x="ats_score",
            nbins=10,
            title="ATS Score Distribution",
            color_discrete_sequence=["#1f77b4"],
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    skill_counter: Counter[str] = Counter()
    for skills in df["skills"].tolist():
        if isinstance(skills, list):
            skill_counter.update(str(skill) for skill in skills)
    top_skills = skill_counter.most_common(10)
    if top_skills:
        skill_df = pd.DataFrame(top_skills, columns=["Skill", "Frequency"])
        fig_skills = px.bar(
            skill_df,
            x="Skill",
            y="Frequency",
            title="Top Skills Across Uploaded Resumes",
            color="Frequency",
            color_continuous_scale="Mint",
        )
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("Skill analytics will appear after parsing resumes with extractable text.")


def _render_comparison_tab(df: pd.DataFrame) -> None:
    st.markdown("### Candidate Comparison")
    candidates = st.multiselect(
        "Select up to 3 candidates",
        options=df["name"].tolist(),
        default=df["name"].tolist()[:2],
    )
    if not candidates:
        st.info("Select candidates to compare.")
        return

    compare_df = df[df["name"].isin(candidates)].copy()
    compare_columns = ["name", "ats_score", "experience_years", "skill_match", "semantic_similarity", "selection_probability"]
    st.dataframe(compare_df[compare_columns], use_container_width=True)

    radar_metrics = ["skill_match", "semantic_similarity", "experience_match", "education_match", "quality_score"]
    fig = go.Figure()
    for _, row in compare_df.iterrows():
        values = [float(row.get(metric, 0)) for metric in radar_metrics]
        values.append(values[0])
        labels = ["Skill", "Semantic", "Experience", "Education", "Quality", "Skill"]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels,
                fill="toself",
                name=str(row.get("name", "Candidate")),
            )
        )
    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        showlegend=True,
        title="Candidate Radar Comparison",
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_role_comparison_tab() -> None:
    st.markdown("### Role Comparison (Saved Jobs)")
    owner = st.session_state.get("auth_user")
    parsed_candidates = st.session_state.get("parsed_candidates", [])
    if not owner:
        st.info("Login required.")
        return
    if not parsed_candidates:
        st.info("Run screening once to compare the same candidate pool across saved jobs.")
        return

    saved_jobs = list_saved_jobs(owner)
    if not saved_jobs:
        st.info("No saved jobs found. Save at least one JD from the sidebar.")
        return

    job_title_map = {str(job["title"]): int(job["id"]) for job in saved_jobs}
    default_titles = list(job_title_map.keys())[:2]
    selected_titles = st.multiselect(
        "Select saved jobs to compare",
        options=list(job_title_map.keys()),
        default=default_titles,
    )
    if not selected_titles:
        st.info("Select one or more saved jobs.")
        return

    weights = st.session_state.get("last_weights", DEFAULT_WEIGHTS.copy())
    min_score = float(st.session_state.get("last_min_score", 70))
    min_experience = int(st.session_state.get("last_min_experience", 1))

    summary_rows: List[Dict[str, object]] = []
    detail_rows: List[Dict[str, object]] = []

    for title in selected_titles:
        job_id = job_title_map[title]
        saved_job = get_saved_job(owner=owner, job_id=job_id)
        if saved_job is None:
            continue
        jd_data = process_jd(str(saved_job["jd_text"]))

        score_values: List[float] = []
        shortlisted = 0
        top_candidate = ""
        top_score = -1.0

        for candidate in parsed_candidates:
            metrics = score_candidate(candidate, jd_data, weights)
            ats_score = float(metrics.get("ats_score", 0.0))
            score_values.append(ats_score)
            if ats_score >= min_score and int(candidate.get("experience_years", 0)) >= min_experience:
                shortlisted += 1

            if ats_score > top_score:
                top_score = ats_score
                top_candidate = str(candidate.get("name", "Unknown"))

            detail_rows.append(
                {
                    "Job": title,
                    "Candidate": str(candidate.get("name", "Unknown")),
                    "ATS Score": round(ats_score, 2),
                }
            )

        avg_score = round(sum(score_values) / len(score_values), 2) if score_values else 0.0
        summary_rows.append(
            {
                "Job": title,
                "Candidates": len(score_values),
                "Avg ATS": avg_score,
                "Shortlisted": shortlisted,
                "Top Candidate": top_candidate,
                "Top Score": round(top_score, 2) if top_score >= 0 else 0.0,
            }
        )

    if not summary_rows:
        st.warning("No comparison data available.")
        return

    summary_df = pd.DataFrame(summary_rows).sort_values(by="Avg ATS", ascending=False).reset_index(drop=True)
    st.dataframe(summary_df, use_container_width=True)

    fig_avg = px.bar(
        summary_df,
        x="Job",
        y="Avg ATS",
        color="Avg ATS",
        color_continuous_scale="Blues",
        title="Average ATS by Saved Job",
    )
    st.plotly_chart(fig_avg, use_container_width=True)

    detail_df = pd.DataFrame(detail_rows)
    pivot_df = detail_df.pivot(index="Candidate", columns="Job", values="ATS Score")
    fig_heat = px.imshow(
        pivot_df,
        aspect="auto",
        color_continuous_scale="Teal",
        title="Candidate vs Job Score Heatmap",
    )
    st.plotly_chart(fig_heat, use_container_width=True)


def _render_dashboard(df: pd.DataFrame) -> str:
    total = len(df)
    shortlisted = int((df["status"] == "Shortlisted").sum())
    avg_score = float(df["ats_score"].mean()) if total else 0.0
    avg_probability = float(df["selection_probability"].mean()) if total else 0.0

    st.markdown(
        """
        <div class="page-head">
          <h1>AI-Powered Resume Intelligence &amp; Filtering System</h1>
          <p>Smart Candidate Evaluation &amp; Hiring Platform</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_metric_cards(total, shortlisted, avg_score, avg_probability)
    st.write("")

    display_df = _filter_candidates_view(df)
    if display_df.empty:
        st.warning("No candidates match current view filters.")
        return df["name"].iloc[0]

    select_options = display_df["name"].tolist()
    default_name = st.session_state.get("selected_name")
    default_index = select_options.index(default_name) if default_name in select_options else 0
    selected_name = st.selectbox("Candidate Detail", select_options, index=default_index)
    selected_row = display_df[display_df["name"] == selected_name].iloc[0].to_dict()

    top_left, top_right = st.columns([2.8, 1.2])

    with top_left:
        st.subheader("Top Candidates")
        table_df = display_df.copy()
        table_df["ATS Score"] = table_df["ats_score"].astype(float)
        table_df["Skill Match"] = table_df["skill_match"].astype(float)
        table_df["Experience"] = table_df["experience_years"].astype(float)
        table_df["Status"] = table_df["status"].astype(str)
        table_df["Action"] = "View"
        table_df = table_df[["rank", "name", "ATS Score", "Skill Match", "Experience", "Status", "Action"]]
        table_df = table_df.rename(columns={"rank": "#", "name": "Candidate"})
        st.data_editor(
            table_df,
            use_container_width=True,
            hide_index=True,
            disabled=True,
            column_config={
                "#": st.column_config.NumberColumn(format="%d"),
                "ATS Score": st.column_config.ProgressColumn("ATS Score", min_value=0, max_value=100, format="%.0f%%"),
                "Skill Match": st.column_config.ProgressColumn("Skill Match", min_value=0, max_value=100, format="%.0f%%"),
                "Experience": st.column_config.NumberColumn("Experience", format="%.0f Years"),
                "Status": st.column_config.TextColumn("Status"),
                "Action": st.column_config.TextColumn("Action"),
            },
        )

    with top_right:
        st.subheader("Skill Match Analysis")
        radar_labels = ["Python", "SQL", "AWS", "Docker", "Communication"]
        matched = {str(skill).lower() for skill in selected_row.get("matched_skills", [])}
        missing = {str(skill).lower() for skill in selected_row.get("missing_skills", [])}
        radar_values = []
        for label in radar_labels:
            lower = label.lower()
            if lower in matched:
                radar_values.append(85)
            elif lower in missing:
                radar_values.append(30)
            else:
                radar_values.append(60)
        radar_values.append(radar_values[0])
        radar_theta = radar_labels + [radar_labels[0]]
        fig_radar = go.Figure(
            data=[
                go.Scatterpolar(
                    r=radar_values,
                    theta=radar_theta,
                    fill="toself",
                    name=selected_name,
                    line={"color": "#2f80ed"},
                )
            ]
        )
        fig_radar.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 100]}}, showlegend=False, margin={"l": 20, "r": 20, "t": 20, "b": 20})
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("**Missing Skills**")
        missing_skills = selected_row.get("missing_skills", [])
        if isinstance(missing_skills, list) and missing_skills:
            st.markdown(
                "".join(f'<span class="badge badge-red">{str(skill)}</span>' for skill in missing_skills[:6]),
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<span class="badge">No major skill gaps</span>', unsafe_allow_html=True)

        st.markdown("**Strengths**")
        matched_skills = selected_row.get("matched_skills", [])
        if isinstance(matched_skills, list) and matched_skills:
            st.markdown(
                "".join(f'<span class="badge badge-green">{str(skill)}</span>' for skill in matched_skills[:6]),
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<span class="badge">General profile match</span>', unsafe_allow_html=True)

        all_csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Report (CSV)", data=all_csv_data, file_name="resume_screening_results.csv", mime="text/csv", use_container_width=True)

    bottom_left, bottom_right = st.columns([2.2, 1.4])
    with bottom_left:
        st.subheader("Candidate Comparison")
        chart_df = display_df.head(6).copy()
        chart_df["Experience Match"] = chart_df["experience_match"].astype(float)
        chart_df = chart_df.rename(columns={"name": "Candidate", "ats_score": "ATS Score", "skill_match": "Skill Match"})
        melt_df = chart_df.melt(
            id_vars=["Candidate"],
            value_vars=["ATS Score", "Skill Match", "Experience Match"],
            var_name="Metric",
            value_name="Score",
        )
        fig_compare = px.bar(
            melt_df,
            x="Candidate",
            y="Score",
            color="Metric",
            barmode="group",
            title="Candidate Comparison",
        )
        fig_compare.update_layout(yaxis_range=[0, 100], legend_title_text="")
        st.plotly_chart(fig_compare, use_container_width=True)

    with bottom_right:
        st.subheader("AI Feedback")
        st.markdown(
            f"""
            <div class="feedback-box">
              <p><b>{selected_name}</b></p>
              <p style="margin:0;"><b>Overall Score:</b> {float(selected_row.get("ats_score", 0)):.1f}%</p>
              <p style="margin:0;"><b>Selection Probability:</b> {float(selected_row.get("selection_probability", 0)):.1f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("**Suggestions**")
        suggestions: List[str] = []
        if isinstance(missing_skills, list) and missing_skills:
            suggestions.append(f"Add project evidence for: {', '.join(str(skill) for skill in missing_skills[:3])}.")
        if float(selected_row.get("quality_score", 0)) < 60:
            suggestions.append("Improve resume quality with quantified impact points.")
        if float(selected_row.get("experience_match", 0)) < 70:
            suggestions.append("Highlight more relevant experience for this role.")
        if not suggestions:
            suggestions.append("Profile is strong; keep resume tailored to this JD.")
        for item in suggestions:
            st.write(f"- {item}")

        if st.button("Generate Interview Questions", use_container_width=True):
            questions = generate_interview_questions(selected_row, st.session_state.get("jd_data", {}))
            st.markdown("**Interview Questions**")
            for index, question in enumerate(questions, start=1):
                st.write(f"{index}. {question}")

    with st.expander("Role Comparison (Saved Jobs)", expanded=False):
        _render_role_comparison_tab()

    return selected_name


def _render_admin_panel() -> None:
    st.markdown(
        """
        <div class="page-head">
          <h1>Admin Control Center</h1>
          <p>Manage users and saved job templates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    users = list_users()
    jobs = list_all_saved_jobs()
    admin_count = sum(1 for user in users if str(user.get("role", "")).lower() == "admin")
    customer_count = sum(1 for user in users if str(user.get("role", "")).lower() == "customer")

    _render_admin_metric_cards(
        total_users=len(users),
        admin_users=admin_count,
        saved_jobs=len(jobs),
        customer_users=customer_count,
    )

    tab_users, tab_jobs = st.tabs(["Users", "Saved Jobs"])
    with tab_users:
        if users:
            users_df = pd.DataFrame(users)
            st.dataframe(users_df, use_container_width=True, hide_index=True)
        else:
            st.info("No users found.")

    with tab_jobs:
        if jobs:
            jobs_df = pd.DataFrame(jobs)
            show_cols = [col for col in ["id", "owner", "title", "created_at"] if col in jobs_df.columns]
            st.dataframe(jobs_df[show_cols], use_container_width=True, hide_index=True)
            selected_job_id = st.selectbox("Delete Saved Job (Admin)", options=[int(job["id"]) for job in jobs])
            if st.button("Delete Selected Job", type="primary"):
                ok, msg = delete_saved_job_admin(selected_job_id)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.info("No saved jobs found.")


def _render_sidebar() -> Dict[str, object]:
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; margin-bottom: 10px;">
              <h2 style="margin-bottom:2px; color:#eaf2fb;">Resume Console</h2>
              <p style="margin-top:0; color:#c5d7ea;">Hiring Intelligence</p>
            </div>
            <div class="sidebar-nav">
              <div class="item active">Dashboard</div>
              <div class="item">Upload Job Description</div>
              <div class="item">Upload Resumes</div>
              <div class="item">Skill Weights</div>
              <div class="item">Candidates List</div>
              <div class="item">Analytics</div>
              <div class="item">Role Recommendations</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"### Logged In: {st.session_state['auth_user']}")
        st.caption(f"Role: {str(st.session_state.get('auth_role', 'customer')).title()}")
        if st.button("Logout", use_container_width=True):
            st.session_state["auth_user"] = None
            st.session_state["auth_role"] = None
            st.session_state["screened_rows"] = []
            st.session_state["parsed_candidates"] = []
            st.session_state["jd_data"] = {}
            st.session_state["selected_name"] = ""
            st.rerun()

        st.write("---")

        st.subheader("Saved Jobs")
        owner = str(st.session_state["auth_user"])
        saved_jobs = list_saved_jobs(owner)
        job_labels = [f"{job['title']} (ID {job['id']})" for job in saved_jobs]
        job_label_to_id = {f"{job['title']} (ID {job['id']})": int(job["id"]) for job in saved_jobs}
        selected_saved_label = st.selectbox("My Saved Jobs", ["None"] + job_labels, key="saved_job_select")
        col_load, col_delete = st.columns(2)
        with col_load:
            if st.button("Load", use_container_width=True):
                if selected_saved_label == "None":
                    st.warning("Select a saved job to load.")
                else:
                    selected_id = job_label_to_id.get(selected_saved_label)
                    if selected_id is None:
                        st.error("Invalid saved job selection.")
                        st.stop()
                    selected_job = get_saved_job(owner=owner, job_id=selected_id)
                    if selected_job is None:
                        st.error("Saved job not found.")
                    else:
                        st.session_state["jd_mode"] = "Paste Text"
                        st.session_state["jd_text_area"] = str(selected_job["jd_text"])
                        st.success(f"Loaded JD: {selected_job['title']}")
                        st.rerun()
        with col_delete:
            if st.button("Delete", use_container_width=True):
                if selected_saved_label == "None":
                    st.warning("Select a saved job to delete.")
                else:
                    selected_id = job_label_to_id.get(selected_saved_label)
                    if selected_id is None:
                        st.error("Invalid saved job selection.")
                        st.stop()
                    ok, message = delete_saved_job(owner=owner, job_id=selected_id)
                    if ok:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        st.write("---")

        st.subheader("Job Description")
        jd_mode = st.radio("JD Input Mode", ["Paste Text", "Upload File"], horizontal=True, key="jd_mode")
        jd_text = ""
        if jd_mode == "Paste Text":
            jd_text = st.text_area(
                "Paste JD",
                height=180,
                placeholder="Paste the full job description...",
                key="jd_text_area",
            )
        else:
            jd_file = st.file_uploader("Upload JD (.txt/.pdf/.docx)", type=["txt", "pdf", "docx"], key="jd")
            if jd_file is not None:
                jd_text = _read_jd_text(jd_file)

        save_col, title_col = st.columns([1, 2])
        with title_col:
            save_title = st.text_input("Save current JD as", placeholder="Example: Backend Python Developer")
        with save_col:
            save_clicked = st.button("Save JD", use_container_width=True)
        if save_clicked:
            if not jd_text.strip():
                st.warning("Enter or load a JD before saving.")
            else:
                ok, message = create_saved_job(owner=owner, title=save_title, jd_text=jd_text)
                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        st.subheader("Resumes")
        resume_files = st.file_uploader(
            "Upload resumes (.pdf/.docx)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="resumes",
        )

        st.subheader("Filters")
        min_score = st.slider("Minimum ATS Score", 0, 100, 70)
        min_experience = st.slider("Minimum Experience (Years)", 0, 20, 1)
        required_skill_filter = st.multiselect("Must-have Skills", SKILL_CATALOG)

        st.subheader("Score Weights")
        w_skill = st.slider("Skill Match %", 0, 100, int(DEFAULT_WEIGHTS["skill"] * 100))
        w_semantic = st.slider("Semantic Similarity %", 0, 100, int(DEFAULT_WEIGHTS["semantic"] * 100))
        w_experience = st.slider("Experience Match %", 0, 100, int(DEFAULT_WEIGHTS["experience"] * 100))
        w_education = st.slider("Education Match %", 0, 100, int(DEFAULT_WEIGHTS["education"] * 100))
        w_quality = st.slider("Resume Quality %", 0, 100, int(DEFAULT_WEIGHTS["quality"] * 100))

        run_clicked = st.button("Run Screening", type="primary", use_container_width=True)

        rows = st.session_state.get("screened_rows", [])
        total = len(rows)
        shortlisted = sum(1 for row in rows if str(row.get("status", "")) == "Shortlisted")
        rejected = total - shortlisted
        st.markdown(
            f"""
            <div class="panel-card">
              <div class="metric-label">System Stats</div>
              <p style="margin:4px 0 0 0;"><b>Total Resumes:</b> {total}</p>
              <p style="margin:2px 0;"><b>Shortlisted:</b> {shortlisted}</p>
              <p style="margin:2px 0;"><b>Rejected:</b> {rejected}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "jd_text": jd_text,
        "resume_files": resume_files,
        "min_score": min_score,
        "min_experience": min_experience,
        "required_skill_filter": required_skill_filter,
        "weights": {
            "skill": w_skill,
            "semantic": w_semantic,
            "experience": w_experience,
            "education": w_education,
            "quality": w_quality,
        },
        "run_clicked": run_clicked,
    }


def main() -> None:
    st.set_page_config(page_title="Resume Intelligence Portal", layout="wide", initial_sidebar_state="expanded")
    _inject_theme()
    _init_state()
    init_auth_db()
    init_job_db()

    if not st.session_state["auth_user"]:
        _render_auth_screen()
        st.stop()

    if str(st.session_state.get("auth_role", "customer")).lower() == "admin":
        with st.sidebar:
            st.markdown(f"### Logged In: {st.session_state['auth_user']}")
            st.caption("Role: Admin")
            if st.button("Logout", use_container_width=True):
                st.session_state["auth_user"] = None
                st.session_state["auth_role"] = None
                st.rerun()
        _render_admin_panel()
        st.stop()

    inputs = _render_sidebar()

    if inputs["run_clicked"]:
        jd_text = str(inputs["jd_text"])
        resume_files = inputs["resume_files"]
        if not jd_text.strip():
            st.warning("Please provide a job description.")
            st.stop()
        if not resume_files:
            st.warning("Please upload at least one resume.")
            st.stop()

        jd_data = process_jd(jd_text)
        required_skill_filter = inputs["required_skill_filter"]
        if required_skill_filter:
            jd_data["required_skills"] = sorted(set(required_skill_filter))

        weights = _build_weights(inputs["weights"])
        processed_rows: List[Dict[str, object]] = []
        parsed_candidates: List[Dict[str, object]] = []

        with st.spinner("Parsing resumes and computing ATS scores..."):
            for resume in resume_files:
                try:
                    candidate = parse_resume_file(resume)
                    parsed_candidates.append(candidate)
                    metrics = score_candidate(candidate, jd_data, weights)
                    row = {
                        "name": candidate["name"],
                        "file_name": candidate["file_name"],
                        "skills": candidate["skills"],
                        "experience_years": candidate["experience_years"],
                        "education": candidate["education"],
                        "text_length": candidate.get("text_length", 0),
                        "parse_warning": candidate.get("parse_warning", ""),
                        **metrics,
                    }
                    processed_rows.append(row)
                except Exception as exc:
                    processed_rows.append(
                        {
                            "name": Path(resume.name).stem,
                            "file_name": resume.name,
                            "skills": [],
                            "experience_years": 0,
                            "education": "unknown",
                            "text_length": 0,
                            "parse_warning": f"Parsing failed: {exc}",
                            "ats_score": 0.0,
                            "skill_match": 0.0,
                            "semantic_similarity": 0.0,
                            "experience_match": 0.0,
                            "education_match": 0.0,
                            "quality_score": 0.0,
                            "matched_skills": [],
                            "missing_skills": [],
                            "quality_feedback": ["Could not parse this file."],
                        }
                    )

        processed_rows = filter_candidates(
            processed_rows,
            min_score=float(inputs["min_score"]),
            min_experience=int(inputs["min_experience"]),
            required_skills=required_skill_filter,
        )
        for row in processed_rows:
            row.update(explain_decision(row))

        st.session_state["screened_rows"] = processed_rows
        st.session_state["parsed_candidates"] = parsed_candidates
        st.session_state["jd_data"] = jd_data
        st.session_state["last_weights"] = weights
        st.session_state["last_min_score"] = float(inputs["min_score"])
        st.session_state["last_min_experience"] = int(inputs["min_experience"])

    if st.session_state["screened_rows"]:
        df = pd.DataFrame(st.session_state["screened_rows"]).sort_values(by="ats_score", ascending=False).reset_index(drop=True)
        df.index = df.index + 1
        df.insert(0, "rank", df.index)

        warning_series = df["parse_warning"] if "parse_warning" in df.columns else pd.Series([], dtype=str)
        warnings = [w for w in warning_series.tolist() if isinstance(w, str) and w.strip()]
        if warnings:
            st.warning(
                "Some resumes had low extracted text. If scoring looks wrong, upload text-based PDF/DOCX instead of scanned images."
            )

        selected_name = _render_dashboard(df)
        st.session_state["selected_name"] = selected_name
    else:
        st.info("Provide JD and resumes in the sidebar, then click Run Screening.")


if __name__ == "__main__":
    main()
