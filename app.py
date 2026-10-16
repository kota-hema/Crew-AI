"""Streamlit interface for the campus cafe launch brief crew."""

import os
import re
from pathlib import Path
from unittest.mock import patch

import streamlit as st
from dotenv import load_dotenv

from campus_cafe.crew import build_crew
from campus_cafe.dataset import load_student_spending


ROOT = Path(__file__).resolve().parent
BRIEF_PATH = ROOT / "final_brief.md"

load_dotenv(ROOT / ".env")
st.set_page_config(page_title="Campus Cafe Launch Brief", page_icon=None, layout="wide")
st.markdown(
    """
    <style>
    :root {
        --ink: #202923;
        --muted: #667269;
        --paper: #fbfcf8;
        --wash: #f0f3ec;
        --line: #d8ded5;
        --accent: #28664b;
    }
    [data-testid="stAppViewContainer"] { background: var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background: var(--wash); border-right: 1px solid var(--line); }
    h1, h2, h3 { color: var(--ink); font-family: Georgia, serif; letter-spacing: 0; }
    h1 { font-size: 2.2rem; }
    [data-testid="stMetricValue"] { color: var(--accent); }
    div.stButton > button[kind="primary"] { background: var(--accent); border-color: var(--accent); }
    a { color: var(--accent); }
    </style>
    """,
    unsafe_allow_html=True,
)

if "brief" not in st.session_state:
    st.session_state.brief = BRIEF_PATH.read_text(encoding="utf-8") if BRIEF_PATH.exists() else ""
    st.session_state.is_live = False
if "is_live" not in st.session_state:
    st.session_state.is_live = False

with st.sidebar:
    st.markdown("### Brief controls")
    process_label = st.radio("Crew process", ("Sequential", "Hierarchical"), horizontal=True)
    api_key = st.text_input(
        "OpenAI API key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Used only for this run. It is not written to the project files.",
    )
    run_clicked = st.button(
        "Research and review",
        type="primary",
        width="stretch",
        disabled=not api_key,
    )
    if not api_key:
        st.caption("Add an API key to start a live agent run.")
    st.divider()
    st.caption("Scenario input: 8,000 students")
    st.caption("The bundled Kaggle dataset is fictional and is not used as evidence.")

if run_clicked:
    try:
        with st.spinner("Researching sources, calculating break-even, and reviewing the draft…"):
            with patch.dict(os.environ, {"OPENAI_API_KEY": api_key}):
                result = build_crew(process_label.lower()).kickoff(inputs={"student_count": 8000})
        brief = str(result).strip()
        if not brief:
            raise ValueError("The reviewer returned an empty brief.")
        if "http://" not in brief and "https://" not in brief:
            raise ValueError("The reviewed brief contains no source URLs.")
        st.session_state.brief = brief
        st.session_state.is_live = True
        st.session_state.run_error = ""
    except Exception as error:
        st.session_state.run_error = type(error).__name__

st.title("Campus cafe launch brief")
st.caption("Evidence review for the Dean of Student Affairs")

if st.session_state.get("run_error"):
    st.error(f"The crew could not complete the run ({st.session_state.run_error}). Check the API key and network, then try again.")

brief_tab, evidence_tab, dataset_tab, reflection_tab = st.tabs(
    ("Launch brief", "Evidence notes", "Dataset explorer", "Collaboration reflection")
)

with brief_tab:
    if st.session_state.is_live:
        st.success("Live agent output · reviewed")
        if st.button("Save as final_brief.md"):
            BRIEF_PATH.write_text(f"{st.session_state.brief.rstrip()}\n", encoding="utf-8")
            st.toast("Saved final_brief.md")
    else:
        st.info("Showing the committed example brief. Run the crew for refreshed research.")
    source_count = len(set(re.findall(r"https?://[^\s)\]]+", st.session_state.brief)))
    metric_columns = st.columns(3)
    metric_columns[0].metric("Scenario enrollment", "8,000")
    metric_columns[1].metric("Example break-even", "4,839 / month")
    metric_columns[2].metric("Sources in brief", str(source_count))
    st.divider()
    st.markdown(st.session_state.brief)
    st.download_button(
        "Download Markdown",
        data=st.session_state.brief,
        file_name="final_brief.md",
        mime="text/markdown",
    )

with evidence_tab:
    st.subheader("Evidence boundaries")
    st.markdown(
        """
        The example brief uses cited public sources for national context and labels all operating figures as assumptions. Campus demand, local menu prices, and vendor costs still need local validation.

        The Kaggle student-spending file contains fictional records, according to its publisher. It is retained for data-ingestion practice only and is not treated as evidence about real students.
        """
    )
    dataset_note = ROOT / "data" / "raw" / "README.md"
    if dataset_note.exists():
        with st.expander("Kaggle dataset details"):
            st.markdown(dataset_note.read_text(encoding="utf-8"))

with dataset_tab:
    st.subheader("Student spending sample")
    st.warning(
        "The publisher identifies every row as fictional. This view describes only the synthetic sample, "
        "not real students or cafe demand. The dataset does not specify the period for its food-expense values."
    )
    dataset = load_student_spending()
    filter_columns = st.columns(2)
    selected_major = filter_columns[0].selectbox(
        "Major", ("All majors", *sorted(dataset["major"].dropna().unique()))
    )
    selected_year = filter_columns[1].selectbox(
        "Year in school", ("All years", *sorted(dataset["year_in_school"].dropna().unique()))
    )
    filtered = dataset
    if selected_major != "All majors":
        filtered = filtered[filtered["major"] == selected_major]
    if selected_year != "All years":
        filtered = filtered[filtered["year_in_school"] == selected_year]

    sample_metrics = st.columns(3)
    sample_metrics[0].metric("Fictional records", f"{len(filtered):,}")
    sample_metrics[1].metric("Food-field mean", f"${filtered['food'].mean():,.2f}")
    sample_metrics[2].metric("Food-field median", f"${filtered['food'].median():,.0f}")
    st.caption("Food amounts are reported in dollars; the time period is unspecified in the dataset description.")

    chart_columns = st.columns(2)
    with chart_columns[0]:
        st.markdown("**Food-field values**")
        bins = filtered["food"].value_counts(bins=10, sort=False).sort_index()
        bins.index = [f"{interval.left:.0f}-{interval.right:.0f}" for interval in bins.index]
        st.bar_chart(bins)
    with chart_columns[1]:
        st.markdown("**Preferred payment method**")
        st.bar_chart(filtered["preferred_payment_method"].value_counts())
    st.markdown("**Sample rows**")
    st.dataframe(filtered.head(20), hide_index=True, width="stretch")

with reflection_tab:
    reflection_path = ROOT / "reflection.md"
    if reflection_path.exists():
        st.markdown(reflection_path.read_text(encoding="utf-8"))