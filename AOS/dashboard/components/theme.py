"""Injects the AOS Command Center theme and configures shared page chrome."""

import streamlit as st

from utils.paths import dashboard_path


def apply_page_config(title: str, icon: str = "■"):
    st.set_page_config(page_title=f"{title} — AOS Command Center", page_icon=icon, layout="wide")
    inject_css()


def inject_css():
    css_path = dashboard_path("assets", "style.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def status_pill(label: str, kind: str = "idle") -> str:
    """kind: ok | warn | fail | idle"""
    return f'<span class="aos-status-pill aos-status-{kind}">{label}</span>'
