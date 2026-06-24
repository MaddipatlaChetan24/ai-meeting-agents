import streamlit as st

st.set_page_config(page_title="Raw Transcript", page_icon="📄", layout="wide")

if not st.session_state.get("processed", False):
    st.warning("Please upload and process a meeting on the Home page first.")
    st.stop()

st.markdown("## 📄 Transcript & Media")
st.markdown("Watch the recording and review the full AI-generated transcript.")

col_player, col_text = st.columns([1, 2])

with col_player:
    if st.session_state.get("youtube_url"):
        st.video(st.session_state["youtube_url"])
    elif st.session_state.get("audio_bytes"):
        st.audio(st.session_state["audio_bytes"])

with col_text:
    st.text_area(
        "Transcript", 
        st.session_state.get("transcript", ""), 
        height=600, 
        label_visibility="collapsed"
    )
