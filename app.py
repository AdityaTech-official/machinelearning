"""Agentic AI Job Application Assistant - Streamlit entry point.

Run with:
    streamlit run app.py

The application starts even when no LLM credentials are configured: every AI
feature falls back to a deterministic, rule-based engine.
"""

from __future__ import annotations

import logging

import streamlit as st

from agents.orchestrator import Orchestrator
from config.settings import active_llm_label, llm_configured
from database.repository import ApplicationRepository
from ui import assistant_page, dashboard, jobs_page, resume_page, tracker_page

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

PAGES = {
    "Dashboard": dashboard.render,
    "Resume Analyzer": resume_page.render,
    "Job Matcher": jobs_page.render,
    "Cover Letter & Skill Gap": assistant_page.render,
    "Application Tracker": tracker_page.render,
}


@st.cache_resource
def get_repository() -> ApplicationRepository:
    """Create a single, cached repository instance (initialises the DB)."""
    return ApplicationRepository()


@st.cache_resource
def get_orchestrator() -> Orchestrator:
    """Create a single, cached orchestrator wired to the repository."""
    return Orchestrator(repository=get_repository())


def main() -> None:
    """Configure the page and dispatch to the selected UI page."""
    st.set_page_config(
        page_title="Agentic AI Job Application Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    repo = get_repository()
    orchestrator = get_orchestrator()

    with st.sidebar:
        st.title("🤖 Job Assistant")
        st.caption("Agentic AI for your job search")

        choice = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
        st.divider()

        badge = "AI enabled" if llm_configured() else "Deterministic mode"
        st.markdown(f"**Engine:** {badge}")
        st.caption(active_llm_label())
        st.divider()
        st.caption(
            "Data stored locally in `data/applications.db`. Resume text is sent "
            "to a model only when an API key is configured."
        )

    renderer = PAGES[choice]
    if choice == "Dashboard":
        renderer(repo)
    elif choice == "Application Tracker":
        renderer(repo, orchestrator)
    else:
        renderer(orchestrator)


if __name__ == "__main__":
    main()
