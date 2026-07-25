"""Dataframe rendering helpers for showing runtime output as tables."""

import pandas as pd
import streamlit as st


def show_table(records: list, columns: list[str] = None, empty_message: str = "No data yet."):
    if not records:
        st.info(empty_message)
        return
    df = pd.DataFrame(records)
    if columns:
        present = [c for c in columns if c in df.columns]
        df = df[present]
    st.dataframe(df, use_container_width=True, hide_index=True)
