"""Small Streamlit session-state helpers, shared across pages."""

import streamlit as st


def get(key, default=None):
    return st.session_state.get(key, default)


def set(key, value):
    st.session_state[key] = value


def bump_refresh():
    """Called after a runtime finishes running, so pages re-read output files
    instead of showing a cached view from before the run."""
    st.session_state["refresh_token"] = st.session_state.get("refresh_token", 0) + 1
