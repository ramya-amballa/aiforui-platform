import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_text_safe, resolve_dated
from components.theme import apply_page_config
from utils.paths import dashboard_path

apply_page_config("Reports", "⇩")

st.title("Reports")
st.caption("Download the reports every AI employee already writes to disk — nothing here is regenerated or recomputed, only read.")

manifest = json.loads(dashboard_path("config", "runtimes.json").read_text(encoding="utf-8"))
reports = manifest.get("reports", {})

for label, relpath_template in reports.items():
    relpath = resolve_dated(relpath_template)
    text, exists = load_text_safe(relpath)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{label}**")
        st.caption(relpath)
    with col2:
        if exists:
            st.download_button("Download", data=text, file_name=Path(relpath).name, mime="text/markdown", key=label)
        else:
            st.button("Not available", disabled=True, key=f"{label}-disabled")
    st.divider()
