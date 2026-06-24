import streamlit as st
from utils.pipeline import import_pipeline

st.set_page_config(page_title="Ask AI", page_icon="💬", layout="wide")

if not st.session_state.get("processed", False):
    st.warning("Please upload and process a meeting on the Home page first.")
    st.stop()

pipe = import_pipeline()

st.markdown("## 💬 Ask AI")
st.markdown("Chat interactively with the meeting transcript using RAG (Retrieval-Augmented Generation).")

for msg in st.session_state.get("chat_history", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_q := st.chat_input("e.g. What deadlines were mentioned?"):
    st.session_state["chat_history"].append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                answer = pipe["ask_question"](st.session_state["rag_chain"], user_q)
            except Exception as e:
                answer = f"Sorry, I encountered an error: {e}"
            st.markdown(answer)
            st.session_state["chat_history"].append({"role": "assistant", "content": answer})
