"""
AI Meeting Assistant — Streamlit UI
====================================
Hackathon Winning Edition
Transcribe, summarise, extract insights and chat with your meetings.
"""


   
        color: #F1F5F9;
    }

    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        flex: 1;
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-2px); border-color: rgba(59,130,246,0.5); }
    .metric-card .value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #3B82F6;
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    }
    
    @keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
    .fade-in { animation: fadeInUp 0.6s ease-out; }

    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.78rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #1E293B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner=False)
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ── Session-state defaults ───────────────────────────────────────────────────
_defaults = {
    "processed": False,
    "title": "",
    "transcript": "",
    "summary": "",
    "actions": "",
    "decisions": "",
    "questions": "",
    "rag_chain": None,
    "chat_history": [],
    "sentiment_data": None,
    "word_cloud": None,
    "keyword_freq": None,
    "meeting_stats": None,
    "follow_up_email": "",
    "youtube_url": "",
    "audio_bytes": None
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎙️ AI Meeting Assistant")
    st.markdown(
        '<p class="hero-subtitle" style="font-size:0.9rem">Hackathon Edition</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    input_mode = st.radio(
        "Input source",
        ["🔗 YouTube URL", "📁 Upload file"],
        horizontal=True,
        label_visibility="collapsed",
    )

    youtube_url = ""
    uploaded_file = None

    if input_mode == "🔗 YouTube URL":
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload audio / video",
            type=["mp3", "mp4", "wav", "m4a", "webm", "ogg", "flac"],
        )

    language = st.selectbox(
        "Audio language",
        ["English", "Hinglish (Hindi + English)"],
        help="Hinglish uses Sarvam AI and requires a SARVAM_API_KEY.",
    )
    lang_key = "hinglish" if "Hinglish" in language else "english"

    st.divider()

    can_process = False
    if input_mode == "🔗 YouTube URL" and youtube_url.strip() and "youtube.com" in youtube_url:
        can_process = True
    elif input_mode == "📁 Upload file" and uploaded_file is not None:
        can_process = True

    process_btn = st.button(
        "🚀 Process Meeting",
        use_container_width=True,
        disabled=not can_process,
        type="primary",
    )

    if not can_process:
        if input_mode == "🔗 YouTube URL" and youtube_url.strip() and "youtube.com" not in youtube_url:
             st.error("Please enter a valid YouTube URL.")
        else:
             st.info("Paste a valid YouTube URL or upload a file.")

    st.divider()
    st.markdown(
        """
        <div style="text-align:center; color:#64748B; font-size:0.75rem;">
        Powered by LangChain • Mistral • Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
if process_btn:
    pipe = import_pipeline()

    # Reset state
    for k in _defaults:
        st.session_state[k] = _defaults[k]
        
    if youtube_url:
        st.session_state["youtube_url"] = youtube_url
    if uploaded_file:
        st.session_state["audio_bytes"] = uploaded_file.getvalue()

    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1
        status_text.markdown("### 🔄 1/7: Downloading audio...")
        if youtube_url.strip():
            chunks = pipe["process_input"](youtube_url.strip())
        else:
            suffix = os.path.splitext(uploaded_file.name)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="downloads")
            os.makedirs("downloads", exist_ok=True)
            tmp.write(uploaded_file.read())
            tmp.close()
            wav_path = pipe["convert_to_wav"](tmp.name)
            chunks = pipe["chunk_audio"](wav_path)
        progress_bar.progress(15)

        # Step 2
        status_text.markdown(f"### 🗣️ 2/7: Transcribing with {'Sarvam' if lang_key=='hinglish' else 'Whisper'}...")
        transcript = pipe["transcribe_all"](chunks, language=lang_key)
        st.session_state["transcript"] = transcript
        progress_bar.progress(35)

        # Step 3
        status_text.markdown("### 📝 3/7: Generating Summary...")
        title = pipe["generate_title"](transcript)
        st.session_state["title"] = title
        summary = pipe["summarize"](transcript)
        st.session_state["summary"] = summary
        progress_bar.progress(50)

        # Step 4
        status_text.markdown("### 🔍 4/7: Extracting Action Items...")
        st.session_state["actions"] = pipe["extract_action_items"](transcript)
        st.session_state["decisions"] = pipe["extract_key_decisions"](transcript)
        st.session_state["questions"] = pipe["extract_questions"](transcript)
        progress_bar.progress(65)

        # Step 5
        status_text.markdown("### 📊 5/7: Analyzing Sentiment & Stats...")
        st.session_state["sentiment_data"] = pipe["analyze_sentiment"](transcript)
        st.session_state["word_cloud"] = pipe["generate_word_cloud"](transcript)
        st.session_state["keyword_freq"] = pipe["get_keyword_frequency"](transcript)
        st.session_state["meeting_stats"] = pipe["get_meeting_stats"](transcript)
        progress_bar.progress(80)

        # Step 6
        status_text.markdown("### 📧 6/7: Drafting Follow-up Email...")
        st.session_state["follow_up_email"] = pipe["generate_follow_up_email"](
            title, summary, st.session_state["actions"], st.session_state["decisions"]
        )
        progress_bar.progress(90)

        # Step 7
        status_text.markdown("### 🧠 7/7: Building Knowledge Base...")
        st.session_state["rag_chain"] = pipe["build_rag_chain"](transcript)
        progress_bar.progress(100)
        
        status_text.empty()
        progress_bar.empty()
        st.toast('Meeting processing complete!', icon='🚀')
        st.session_state["processed"] = True

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        st.exception(e)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT — Landing Page
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state["processed"]:
    pipe = import_pipeline()
    st_lottie = pipe["st_lottie"]
    lottie_url = "https://assets3.lottiefiles.com/packages/lf20_q5pk6p1k.json" # Tech/AI animation
    lottie_json = load_lottieurl(lottie_url)

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<br><br>', unsafe_allow_html=True)
        st.markdown('<h1 class="hero-title">AI Meeting Assistant</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="hero-subtitle">'
            "Transform any meeting recording into actionable insights in minutes. <br>"
            "Powered by advanced LLMs, sentiment analysis, and interactive analytics."
            "</p>",
            unsafe_allow_html=True,
        )
    with c2:
        if lottie_json:
            st_lottie(lottie_json, height=300, key="hero_lottie")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    features = [
        ("📊", "Deep Analytics", "Sentiment timeline, word clouds, and speaking stats.", "pages/1_📊_Deep_Analytics.py"),
        ("📝", "Smart Summaries", "Map-reduce summaries and structured action items.", "pages/2_📝_Smart_Summaries.py"),
        ("📧", "Follow-ups", "AI-drafted professional emails ready to send.", "pages/3_📧_Follow_Ups.py"),
        ("💬", "Ask AI", "RAG-powered interactive Q&A over your meeting.", "pages/4_💬_Ask_AI.py"),
    ]
    for col, (icon, label, desc, page_url) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(
                f"""
                <div class="glass-card" style="text-align:center; min-height:180px;">
                    <div style="font-size:2.4rem; margin-bottom:0.5rem;">{icon}</div>
                    <h3 style="margin-bottom:0.3rem;">{label}</h3>
                    <p style="color:#94A3B8; font-size:0.85rem;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            try:
                st.page_link(page_url, label=f"Go to {label}", icon="➡️")
            except:
                pass

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT — Results
# ═══════════════════════════════════════════════════════════════════════════════
else:
    # ── Title bar ────────────────────────────────────
    st.markdown(
        f'<div class="fade-in"><h1 class="hero-title">{st.session_state["title"]}</h1></div>',
        unsafe_allow_html=True,
    )

    st.success("🎉 Processing complete! Choose a page from the sidebar to explore your insights.")

    # ── Export buttons ───────────────────────────────
    exp_col1, exp_col2, _ = st.columns([1, 1, 4])
    with exp_col1:
        pdf_path = cached_export_to_pdf(
            st.session_state["title"],
            st.session_state["summary"],
            st.session_state["actions"],
            st.session_state["decisions"],
            st.session_state["questions"],
            st.session_state["transcript"],
        )
        with open(pdf_path, "rb") as f:
            st.download_button("📥 PDF Report", data=f, file_name="meeting_report.pdf", mime="application/pdf", use_container_width=True)
    with exp_col2:
        txt_path = cached_export_to_txt(
            st.session_state["title"],
            st.session_state["summary"],
            st.session_state["actions"],
            st.session_state["decisions"],
            st.session_state["questions"],
            st.session_state["transcript"],
        )
        with open(txt_path, "rb") as f:
            st.download_button("📥 Text Report", data=f, file_name="meeting_report.txt", mime="text/plain", use_container_width=True)

    st.divider()

    st.markdown("### Quick Navigation")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.page_link("pages/1_📊_Deep_Analytics.py", label="Deep Analytics", icon="📊")
    with c2: st.page_link("pages/2_📝_Smart_Summaries.py", label="Smart Summaries", icon="📝")
    with c3: st.page_link("pages/3_📧_Follow_Ups.py", label="Follow-ups", icon="📧")
    with c4: st.page_link("pages/4_💬_Ask_AI.py", label="Ask AI", icon="💬")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer">
        AI Meeting Assistant · Hackathon Edition · Built with LangChain & Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
