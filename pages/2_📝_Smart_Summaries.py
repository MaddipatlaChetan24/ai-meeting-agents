import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Smart Summaries", page_icon="📝", layout="wide")

if not st.session_state.get("processed", False):
    st.warning("Please upload and process a meeting on the Home page first.")
    st.stop()

st.markdown("## 📝 Smart Summaries")

st.markdown("### Executive Summary")
st.info(st.session_state.get("summary", "No summary available."))

st.markdown("### ✅ Action Items")
actions_str = st.session_state.get("actions", "")
try:
    actions_json = json.loads(actions_str)
    if actions_json:
        df = pd.DataFrame(actions_json)
        st.data_editor(
            df,
            column_config={
                "task": "Task Description",
                "owner": "Owner",
                "deadline": "Deadline",
                "priority": st.column_config.SelectboxColumn("Priority", options=["High", "Medium", "Low"])
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No action items found.")
except:
    # Fallback to plain text
    st.markdown(actions_str)

st.markdown("### 🔑 Key Decisions")
st.success(st.session_state.get("decisions", "No decisions found."))

st.markdown("### ❓ Unresolved Questions")
st.warning(st.session_state.get("questions", "No questions found."))
