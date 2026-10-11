"""
app.py
======

ResumeIQ - Smart Resume Analyzer (Streamlit user interface).

This file is ONLY the user interface. All of the real analysis logic lives in
`analyzer.py`, and all the embedded sample text lives in `sample_data.py`. This
clean separation makes the project easy to explain and easy to test.

Run with:
    streamlit run app.py

Academic note: every score shown here is a transparent, rule-based keyword
indicator for educational / preliminary screening only. It is NOT a prediction
of hiring success and NOT a guarantee of ATS compatibility.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import analyzer
from sample_data import (
    ROLE_SAMPLES,
    SAMPLE_JOB_DESCRIPTIONS,
    SAMPLE_RESUMES,
    SKILL_DATABASE,
)

# ---------------------------------------------------------------------------
# Page configuration (must be the first Streamlit call).
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ResumeIQ - Smart Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

DISCLAIMER = (
    "ResumeIQ is an academic demonstration. All scores are rule-based keyword "
    "indicators for educational and preliminary screening only - not a "
    "prediction of hiring success and not a guarantee of ATS compatibility. "
    "Always apply human judgement."
)


# ---------------------------------------------------------------------------
# Small UI helper functions
# ---------------------------------------------------------------------------
def gauge_chart(value, title):
    """Return a Plotly gauge for a 0-100 score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#2563eb"},
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fef9c3"},
                {"range": [70, 100], "color": "#dcfce7"},
            ],
        },
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def matched_missing_bar(keyword_match):
    """Bar chart of matched vs missing keyword counts."""
    fig = go.Figure(go.Bar(
        x=["Matched", "Missing"],
        y=[keyword_match["matched_count"], keyword_match["missing_count"]],
        marker_color=["#16a34a", "#dc2626"],
        text=[keyword_match["matched_count"], keyword_match["missing_count"]],
        textposition="auto",
    ))
    fig.update_layout(height=300, title="Required keywords: matched vs missing",
                      yaxis_title="Count", margin=dict(l=20, r=20, t=50, b=20))
    return fig


def category_coverage_chart(resume_skills, job_skills):
    """Grouped bar chart of skills per category (resume vs job)."""
    categories = list(SKILL_DATABASE.keys())
    resume_counts = [len(resume_skills.get(cat, [])) for cat in categories]
    job_counts = [len(job_skills.get(cat, [])) for cat in categories]
    fig = go.Figure()
    fig.add_bar(name="Resume", x=categories, y=resume_counts, marker_color="#2563eb")
    fig.add_bar(name="Job Description", x=categories, y=job_counts, marker_color="#f59e0b")
    fig.update_layout(barmode="group", height=360, title="Skill coverage by category",
                      xaxis_tickangle=-30, margin=dict(l=20, r=20, t=50, b=80))
    return fig


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
# The text areas own their own state via their widget keys ("resume_area",
# "job_area", "job_title_input"). We only need to make sure "analysis" exists.
#
# IMPORTANT Streamlit rule used throughout this file:
#   A widget created with a `key` stores its value in st.session_state[key].
#   To fill such a widget programmatically (from an upload or a sample) we must
#   write to that same key BEFORE the widget is created on a rerun - never pass
#   a `value=` argument alongside the key. Loader buttons therefore use
#   `on_click` callbacks, which run at the start of the next rerun (before any
#   widget is instantiated), so the new text is in place when the widget draws.
if "analysis" not in st.session_state:
    st.session_state["analysis"] = None


# --- Callbacks that fill the input widgets (run before widgets instantiate) ---
def _load_sample_resume():
    choice = st.session_state.get("resume_sample_choice")
    if choice:
        st.session_state["resume_area"] = SAMPLE_RESUMES[choice].strip()


def _load_sample_job():
    choice = st.session_state.get("job_sample_choice")
    if choice:
        st.session_state["job_area"] = SAMPLE_JOB_DESCRIPTIONS[choice].strip()
        if not st.session_state.get("job_title_input"):
            st.session_state["job_title_input"] = choice


def _load_role_demo():
    role = st.session_state.get("job_role_choice")
    if role:
        st.session_state["resume_area"] = ROLE_SAMPLES[role]["resume"].strip()
        st.session_state["job_area"] = ROLE_SAMPLES[role]["job_description"].strip()
        st.session_state["job_title_input"] = role


def _reset_all():
    for k in ["resume_area", "job_area", "job_title_input",
              "resume_file", "_resume_file_id", "analysis"]:
        st.session_state.pop(k, None)


# ===========================================================================
# PAGES
# ===========================================================================
def page_home():
    st.title("📄 ResumeIQ - Smart Resume Analyzer")
    st.caption("Resume screening & job-description matching using Python string processing")
    st.info(DISCLAIMER, icon="ℹ️")

    st.markdown(
        """
        ### What this project does
        ResumeIQ compares a **resume** against a **job description** using simple,
        transparent **Python string-processing** techniques - lowercasing,
        regular expressions, a skill dictionary and Python **set** operations -
        to produce an explainable match score and a list of missing skills.

        ### How to use it
        1. Go to **Analyze Resume** in the sidebar.
        2. Choose how to provide the resume: paste text, upload a file, or load
           an embedded sample.
        3. Provide a job description (paste, sample, or by role).
        4. Click **Analyze** and explore the result tabs.

        ### Core Python concepts demonstrated
        - Embedded (triple-quoted) strings for samples & the skill database
        - String cleaning / normalisation and regular expressions
        - Dictionaries, lists and **sets** (intersection / difference)
        - Functions, loops, conditionals and basic data visualisation
        """
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Sample resumes", len(SAMPLE_RESUMES))
    c2.metric("Sample job descriptions", len(SAMPLE_JOB_DESCRIPTIONS))
    c3.metric("Skill categories", len(SKILL_DATABASE))


def resume_input_block():
    """Render the resume-input controls and return the chosen resume text.

    The editable text area (key="resume_area") is the SINGLE SOURCE OF TRUTH.
    Uploads and samples only *fill* it; the two are never silently combined.
    """
    st.subheader("1. Provide the resume")
    method = st.radio(
        "Resume input method",
        ["Paste text", "Upload file", "Use a sample"],
        horizontal=True,
        key="resume_method",
    )

    if method == "Use a sample":
        st.selectbox("Choose a sample resume", list(SAMPLE_RESUMES.keys()),
                     key="resume_sample_choice")
        st.button("Load this sample resume", on_click=_load_sample_resume)

    elif method == "Upload file":
        uploaded = st.file_uploader(
            "Upload a resume (.txt, .pdf, .docx)",
            type=["txt", "pdf", "docx"],
            key="resume_file",
        )
        if uploaded is not None:
            # Only extract once per newly-selected file so later edits are kept.
            file_id = (uploaded.name, uploaded.size)
            if st.session_state.get("_resume_file_id") != file_id:
                try:
                    extracted = analyzer.extract_text_from_file(uploaded)
                    # Write to the widget key BEFORE the text_area is created.
                    st.session_state["resume_area"] = extracted
                    st.session_state["_resume_file_id"] = file_id
                    st.success(
                        f"Extracted text from '{uploaded.name}' "
                        f"({len(extracted.split())} words). Review/edit below."
                    )
                except ValueError as exc:
                    st.error(f"Could not read the file: {exc}")

    st.caption("This editable box is what will be analyzed (upload/sample just fills it).")
    return st.text_area("Resume text", height=260, key="resume_area")


def job_input_block():
    """Render job-description controls and return the chosen job text + title."""
    st.subheader("2. Provide the job description")
    method = st.radio(
        "Job description input method",
        ["Paste text", "Use a sample", "Load by role"],
        horizontal=True,
        key="job_method",
    )

    title = st.text_input("Job title (optional)", key="job_title_input")

    if method == "Use a sample":
        st.selectbox("Choose a sample job description",
                     list(SAMPLE_JOB_DESCRIPTIONS.keys()),
                     key="job_sample_choice")
        st.button("Load this sample job description", on_click=_load_sample_job)

    elif method == "Load by role":
        st.selectbox("Choose a role (loads matching resume + job)",
                     list(ROLE_SAMPLES.keys()), key="job_role_choice")
        st.button("Load resume + job for this role (demo mode)",
                  on_click=_load_role_demo)
        st.caption("Demo mode fills both the resume (above) and the job description.")

    job_text = st.text_area("Job description text", height=200, key="job_area")
    return job_text, title


def page_analyze():
    st.title("🔍 Analyze Resume")
    st.info(DISCLAIMER, icon="ℹ️")

    resume_text = resume_input_block()
    job_text, title = job_input_block()

    col_run, col_reset = st.columns([1, 1])
    with col_run:
        run = st.button("🚀 Analyze", type="primary", use_container_width=True)
    with col_reset:
        # A callback clears the widget keys safely (callbacks run before the
        # widgets are re-instantiated, which is the only time those keys may
        # be modified).
        st.button("♻️ Clear / Reset", use_container_width=True, on_click=_reset_all)

    # Input validation - prevent analysis on empty inputs.
    if run:
        if not resume_text.strip():
            st.error("Please provide resume text before analyzing.")
            return
        if not job_text.strip():
            st.error("Please provide a job description before analyzing.")
            return
        st.session_state["analysis"] = analyzer.analyze_resume(
            resume_text, job_text, job_title=title
        )

    analysis = st.session_state.get("analysis")
    if analysis:
        render_dashboard(analysis)


def render_dashboard(analysis):
    """Render all analysis results in organised tabs."""
    km = analysis["keyword_match"]
    readiness = analysis["readiness"]
    stats = analysis["statistics"]

    st.markdown("---")
    st.header("📊 Analysis Dashboard")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Keyword Match", f"{km['match_percentage']}%")
    m2.metric("Readiness Score", f"{readiness['total']}/100")
    m3.metric("Matched Keywords", km["matched_count"])
    m4.metric("Missing Keywords", km["missing_count"])

    tabs = st.tabs([
        "Overview", "Skills", "Skill Gap", "Quality Checks",
        "Strengths & Suggestions", "Raw vs Clean", "Report",
    ])

    # --- Overview ---
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(gauge_chart(km["match_percentage"], "Keyword Match %"),
                            use_container_width=True)
        with c2:
            st.plotly_chart(gauge_chart(readiness["total"], "Readiness Score"),
                            use_container_width=True)

        st.plotly_chart(matched_missing_bar(km), use_container_width=True)

        with st.expander("How is the Readiness Score calculated?"):
            st.write("The weighted components below always sum to 100%:")
            comp_rows = [
                {
                    "Component": name.replace("_", " ").title(),
                    "Score %": comp["score_pct"],
                    "Weight %": comp["weight"],
                    "Contribution": comp["contribution"],
                }
                for name, comp in readiness["components"].items()
            ]
            st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

        st.subheader("Resume statistics")
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Words", stats["word_count"])
        s2.metric("Characters", stats["character_count"])
        s3.metric("Lines", stats["line_count"])
        s4.metric("Sentences", stats["sentence_count"])
        s5.metric("Avg word len", stats["average_word_length"])

        st.subheader("Contact information (categories only, for privacy)")
        contact = analysis["contact"]
        cc = st.columns(5)
        cc[0].metric("Email", "Yes" if contact["email"]["found"] else "No")
        cc[1].metric("Phone", "Yes" if contact["phone"]["found"] else "No")
        cc[2].metric("LinkedIn", "Yes" if contact["linkedin"]["found"] else "No")
        cc[3].metric("GitHub", "Yes" if contact["github"]["found"] else "No")
        cc[4].metric("Portfolio", "Yes" if contact["portfolio"]["found"] else "No")
        st.caption("Detection is pattern-based and may miss unusual formats or "
                   "produce false positives. Personal details are not displayed.")

        st.subheader("Sections")
        sc1, sc2 = st.columns(2)
        sc1.success("Detected: " + (", ".join(analysis["sections"]["present"]) or "None"))
        sc2.warning("Possibly missing: " + (", ".join(analysis["sections"]["missing"]) or "None"))

    # --- Skills ---
    with tabs[1]:
        st.plotly_chart(
            category_coverage_chart(analysis["resume_skills"], analysis["job_skills"]),
            use_container_width=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Skills detected in resume**")
            st.write(", ".join(sorted(analysis["resume_skills_flat"])) or "None")
        with c2:
            st.markdown("**Skills required by job description**")
            st.write(", ".join(sorted(analysis["job_skills_flat"])) or "None")
        st.markdown("**Matched (in both)**")
        st.success(", ".join(km["matched"]) or "None")
        st.markdown("**Additional skills in resume (not required by job)**")
        st.info(", ".join(km["extra"]) or "None")

    # --- Skill Gap ---
    with tabs[2]:
        st.caption("One row per skill the job description requires.")
        gap_df = pd.DataFrame(analysis["skill_gap"])
        if not gap_df.empty:
            gap_df = gap_df.rename(columns={
                "skill": "Skill", "category": "Category",
                "in_resume": "In Resume", "required_by_job": "Required by Job",
                "recommendation": "Recommendation",
            })
            st.dataframe(gap_df, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Download skill gap (CSV)",
                data=gap_df.to_csv(index=False).encode("utf-8"),
                file_name="skill_gap_analysis.csv",
                mime="text/csv",
            )
        else:
            st.info("No recognised skills were found in the job description.")

    # --- Quality Checks ---
    with tabs[3]:
        st.caption("Heuristic checks - a failing check is a prompt to review, not a penalty.")
        for chk in analysis["quality_checks"]:
            icon = "✅" if chk["passed"] else "⚠️"
            st.write(f"{icon} **{chk['label']}** - {chk['note']}")

        exp_edu = analysis["experience_education"]
        with st.expander("Approximate experience / education signals"):
            st.write("Years of experience (approx):",
                     ", ".join(exp_edu["years_of_experience"]) or "none detected")
            st.write("Degrees (approx):", ", ".join(exp_edu["degrees"]) or "none detected")
            st.write("Graduation years (approx):",
                     ", ".join(exp_edu["graduation_years"]) or "none detected")
            st.caption("These detections are approximate and never invent information.")

    # --- Strengths & Suggestions ---
    with tabs[4]:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Strengths")
            for s in analysis["strengths"]:
                st.write(f"✅ {s}")
        with c2:
            st.subheader("Improvement suggestions")
            for s in analysis["suggestions"]:
                st.write(f"➡️ {s}")

    # --- Raw vs Clean ---
    with tabs[5]:
        st.caption("See exactly what preprocessing does before matching.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Raw resume text**")
            st.code(analysis["raw_text"][:1500] or "(empty)")
        with c2:
            st.markdown("**Cleaned (preprocessed) text**")
            st.code(analyzer.preprocess_text(analysis["raw_text"])[:1500] or "(empty)")

    # --- Report ---
    with tabs[6]:
        report = analyzer.create_analysis_report(analysis)
        st.markdown(report)
        try:
            pdf_bytes = analyzer.create_analysis_pdf(analysis)
            st.download_button(
                "⬇️ Download full report (PDF)",
                data=pdf_bytes,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
            )
        except Exception as exc:  # noqa: BLE001 - surface a friendly message
            st.error(f"Could not generate the PDF report: {exc}")


def page_compare():
    st.title("🆚 Compare Two Resumes")
    st.info(DISCLAIMER, icon="ℹ️")
    st.caption("Measures textual relevance to ONE job description - not an "
               "objective measure of candidate quality.")

    jd_choice = st.selectbox("Job description (sample)", list(SAMPLE_JOB_DESCRIPTIONS.keys()))
    jd_text = st.text_area("Job description",
                           value=SAMPLE_JOB_DESCRIPTIONS[jd_choice].strip(), height=160)

    c1, c2 = st.columns(2)
    with c1:
        r1_choice = st.selectbox("Resume A (sample)", list(SAMPLE_RESUMES.keys()), index=0)
        r1_text = st.text_area("Resume A", value=SAMPLE_RESUMES[r1_choice].strip(), height=220)
    with c2:
        r2_choice = st.selectbox("Resume B (sample)", list(SAMPLE_RESUMES.keys()), index=1)
        r2_text = st.text_area("Resume B", value=SAMPLE_RESUMES[r2_choice].strip(), height=220)

    if st.button("Compare", type="primary"):
        if not r1_text.strip() or not r2_text.strip() or not jd_text.strip():
            st.error("Please provide both resumes and a job description.")
            return
        result = analyzer.compare_resumes(r1_text, r2_text, jd_text,
                                          "Candidate 1", "Candidate 2")
        df = pd.DataFrame(result["summary"]).rename(columns={
            "name": "Candidate",
            "match_percentage": "Match %",
            "matched_count": "Matched",
            "missing_count": "Missing",
            "word_count": "Words",
            "sections_present": "Sections",
            "contact_complete": "Contact OK",
            "readiness": "Readiness",
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        fig = go.Figure(go.Bar(
            x=df["Candidate"], y=df["Match %"],
            marker_color=["#2563eb", "#f59e0b"], text=df["Match %"], textposition="auto",
        ))
        fig.update_layout(title="Keyword match comparison", yaxis_title="Match %", height=320)
        st.plotly_chart(fig, use_container_width=True)


def page_batch():
    st.title("📚 Batch Screening")
    st.info(DISCLAIMER, icon="ℹ️")
    MAX_FILES = 10
    st.caption(f"Upload up to {MAX_FILES} resumes (.txt/.pdf/.docx) to screen "
               "against one job description. Results are labelled by the "
               "resume file name. Rankings reflect textual keyword relevance "
               "only - never sensitive attributes.")

    jd_choice = st.selectbox("Job description (sample)", list(SAMPLE_JOB_DESCRIPTIONS.keys()))
    jd_text = st.text_area("Job description",
                           value=SAMPLE_JOB_DESCRIPTIONS[jd_choice].strip(), height=160)

    uploaded = st.file_uploader("Upload resumes", type=["txt", "pdf", "docx"],
                                accept_multiple_files=True)

    use_samples = st.checkbox("No files handy? Use the 5 embedded sample resumes instead")

    if st.button("Screen resumes", type="primary"):
        if not jd_text.strip():
            st.error("Please provide a job description.")
            return

        resumes = []
        if use_samples:
            # Use the sample's descriptive name as the "resume name".
            for name, text in SAMPLE_RESUMES.items():
                resumes.append((f"{name} (sample)", text))
        else:
            if not uploaded:
                st.error("Please upload at least one resume or tick the sample option.")
                return
            for f in uploaded[:MAX_FILES]:
                try:
                    text = analyzer.extract_text_from_file(f)
                except ValueError as exc:
                    text = ""
                    st.warning(f"{f.name}: {exc}")
                # Label each row by the actual resume file name.
                resumes.append((f.name, text))

        rows = analyzer.analyze_multiple_resumes(resumes, jd_text, max_files=MAX_FILES)
        df = pd.DataFrame(rows).rename(columns={
            "identifier": "Resume",
            "match_percentage": "Match %",
            "matched_keywords": "Matched Keywords",
            "missing_keywords": "Missing Keywords",
            "word_count": "Words",
            "sections_present": "Sections",
            "error": "Error",
        })
        df = df.sort_values("Match %", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download batch results (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="batch_screening_results.csv",
            mime="text/csv",
        )


def page_methodology():
    st.title("🧠 Project Methodology")
    st.markdown(
        """
        ### The algorithm, step by step
        1. **Preprocess** both documents: lowercase, normalise whitespace, and
           keep technology symbols (`c++`, `c#`, `.net`, `node.js`, `ci/cd`).
        2. **Extract skills** using the embedded `SKILL_DATABASE`. Each skill is
           matched with a carefully built regular expression so that, e.g.,
           `"r"` matches the language *R* but not the *r* inside *"react"*.
        3. **Compare with sets**:
           - `matched = resume_skills ∩ job_skills`
           - `missing = job_skills − resume_skills`
        4. **Score**:
           - *Keyword match %* = matched ÷ total job keywords × 100
           - *Readiness score* = weighted blend (keywords 60%, sections 20%,
             contact 10%, readability 10%) - weights always sum to 100%.
        5. **Explain**: generate strengths & suggestions with simple if/else
           rules, each tied to something actually detected.

        ### Why these choices
        - **Streamlit** (not Flask/Django) → a data app with charts and widgets
          in pure Python, no separate frontend.
        - **Sets** → make keyword comparison fast and mathematically clear.
        - **No database** → all data is embedded; nothing needs to persist.
        - **No external AI APIs** → runs fully offline, every number is explainable.
        """
    )
    with st.expander("See the live skill database"):
        for cat, skills in SKILL_DATABASE.items():
            st.write(f"**{cat}**: {', '.join(skills)}")


def page_about():
    st.title("ℹ️ About & Limitations")
    st.markdown(
        """
        ### About
        **ResumeIQ** is a Master of Engineering mini-project demonstrating how
        Python string processing can power a resume screening and
        job-description matching tool.

        ### What it CANNOT do (limitations)
        - It does **not understand meaning** - it matches keywords, not concepts.
          A resume saying *"built ML models"* without the word *"machine learning"*
          may be under-credited (false negative).
        - It cannot judge a candidate's actual **proficiency** or seniority.
        - It cannot guarantee **ATS compatibility**.
        - Contact / section detection is **pattern-based** and can be wrong.
        - Scanned (image-only) PDFs need **OCR**, which is out of scope.

        ### Responsible use
        - Resumes are processed in memory; the app does not permanently store them.
        - It never infers sensitive attributes (gender, age, religion, etc.).
        - Always keep a human in the loop for real hiring decisions.
        """
    )
    st.info(DISCLAIMER, icon="ℹ️")


# ===========================================================================
# SIDEBAR NAVIGATION
# ===========================================================================
PAGES = {
    "🏠 Home": page_home,
    "🔍 Analyze Resume": page_analyze,
    "🆚 Compare Resumes": page_compare,
    "📚 Batch Screening": page_batch,
    "🧠 Methodology": page_methodology,
    "ℹ️ About & Limitations": page_about,
}

st.sidebar.title("ResumeIQ")
st.sidebar.caption("Smart Resume Analyzer")
selection = st.sidebar.radio("Navigate", list(PAGES.keys()))
st.sidebar.markdown("---")
st.sidebar.caption("Academic demonstration project. "
                   "Scores are heuristic indicators only.")

PAGES[selection]()

# Footer
st.markdown("---")
st.caption("ResumeIQ · Academic demonstration · Rule-based keyword analysis, "
           "not a hiring decision tool.")
