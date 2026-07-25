"""Reusable metric-card rendering for the Home dashboard and per-runtime pages."""

import streamlit as st


def metric_card(label: str, value: str, sub: str = ""):
    sub_html = f'<div class="aos-card-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="aos-card">
          <h4>{label}</h4>
          <div class="aos-card-value">{value}</div>
          {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(cards: list[tuple[str, str, str]], columns: int = 5):
    """cards: list of (label, value, sub) tuples, laid out `columns` per row."""
    for start in range(0, len(cards), columns):
        row = cards[start:start + columns]
        cols = st.columns(len(row))
        for col, (label, value, sub) in zip(cols, row):
            with col:
                metric_card(label, value, sub)
