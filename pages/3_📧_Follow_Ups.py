import streamlit as st

st.set_page_config(page_title="Follow-up Email", page_icon="📧", layout="wide")

if not st.session_state.get("processed", False):
    st.warning("Please upload and process a meeting on the Home page first.")
    st.stop()

st.markdown("## 📧 AI Drafted Follow-up")
st.markdown("A professional follow-up email ready to copy and send to your team.")

email_draft = st.session_state.get("follow_up_email", "")

st.text_area("Email Draft", email_draft, height=500, label_visibility="collapsed")
st.button("📋 Copy to Clipboard", on_click=lambda: st.toast("Copied (Not natively supported without streamlit-extras, text is ready to highlight)", icon="📋"))
