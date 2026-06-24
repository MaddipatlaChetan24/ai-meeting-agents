import streamlit as st

@st.cache_resource(show_spinner=False)
def import_pipeline():
    """Import heavy modules once and cache them."""
    from utils.audio_processor import process_input, convert_to_wav, chunk_audio
    from core.transcriber import transcribe_all
    from core.summarizer import summarize, generate_title
    from core.extractor import extract_action_items, extract_key_decisions, extract_questions
    from core.rag_engine import build_rag_chain, ask_question
    from core.sentiment import analyze_sentiment
    from core.analytics import generate_word_cloud, get_keyword_frequency, get_meeting_stats
    from core.email_generator import generate_follow_up_email
    from utils.export import export_to_pdf, export_to_txt
    import plotly.express as px
    import plotly.graph_objects as go
    from streamlit_lottie import st_lottie
    
    return {
        "process_input": process_input,
        "convert_to_wav": convert_to_wav,
        "chunk_audio": chunk_audio,
        "transcribe_all": transcribe_all,
        "summarize": summarize,
        "generate_title": generate_title,
        "extract_action_items": extract_action_items,
        "extract_key_decisions": extract_key_decisions,
        "extract_questions": extract_questions,
        "build_rag_chain": build_rag_chain,
        "ask_question": ask_question,
        "analyze_sentiment": analyze_sentiment,
        "generate_word_cloud": generate_word_cloud,
        "get_keyword_frequency": get_keyword_frequency,
        "get_meeting_stats": get_meeting_stats,
        "generate_follow_up_email": generate_follow_up_email,
        "export_to_pdf": export_to_pdf,
        "export_to_txt": export_to_txt,
        "px": px,
        "go": go,
        "st_lottie": st_lottie
    }

@st.cache_data(show_spinner=False)
def cached_export_to_pdf(title, summary, actions, decisions, questions, transcript):
    pipe = import_pipeline()
    return pipe["export_to_pdf"](title, summary, actions, decisions, questions, transcript)

@st.cache_data(show_spinner=False)
def cached_export_to_txt(title, summary, actions, decisions, questions, transcript):
    pipe = import_pipeline()
    return pipe["export_to_txt"](title, summary, actions, decisions, questions, transcript)
