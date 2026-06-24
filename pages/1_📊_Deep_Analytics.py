import streamlit as st
import pandas as pd
from utils.pipeline import import_pipeline

st.set_page_config(page_title="Deep Analytics", page_icon="📊", layout="wide")

if not st.session_state.get("processed", False):
    st.warning("Please upload and process a meeting on the Home page first.")
    st.stop()

pipe = import_pipeline()
px = pipe["px"]

st.markdown("## 📊 Deep Analytics")
st.markdown("Explore the sentiment arc, word cloud, and speaking statistics from your meeting.")

# ── Metrics row ──────────────────────────────────
stats = st.session_state.get("meeting_stats", {})
sentiment = st.session_state.get("sentiment_data", {}).get("overall", {})

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Words", f"{stats.get('total_words', 0):,}")
with col2:
    st.metric("Estimated Duration", f"{stats.get('estimated_duration_min', 0)} min")
with col3:
    st.metric("Overall Mood", f"{sentiment.get('emoji', '😐')} {sentiment.get('label', 'Neutral')}")

st.divider()

st.markdown("### Topic Cloud & Keywords")
colA, colB = st.columns(2)

with colA:
    if st.session_state.get("word_cloud"):
        st.markdown("#### Topic Cloud")
        st.image(st.session_state["word_cloud"], use_container_width=True)
        
with colB:
    if st.session_state.get("keyword_freq"):
        st.markdown("#### Top Keywords")
        df = pd.DataFrame(st.session_state["keyword_freq"]).head(10)
        fig = px.bar(df, x='count', y='word', orientation='h')
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
        fig.update_traces(marker_color='#3B82F6')
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        
st.divider()

st.markdown("### Emotional Arc")
sent_data = st.session_state.get("sentiment_data", {})
if sent_data and 'timeline' in sent_data:
    timeline = sent_data['timeline']
    df_sent = pd.DataFrame(timeline)
    
    fig2 = px.line(df_sent, x='chunk_index', y='polarity', hover_data=['text_preview', 'label'], markers=True)
    fig2.add_hrect(y0=0.1, y1=1, line_width=0, fillcolor="rgba(34,197,94,0.1)", opacity=0.2)
    fig2.add_hrect(y0=-1, y1=-0.1, line_width=0, fillcolor="rgba(239,68,68,0.1)", opacity=0.2)
    fig2.update_layout(height=400, yaxis_title="Positivity Score", xaxis_title="Timeline Segment")
    fig2.update_traces(line_color='#8B5CF6')
    st.plotly_chart(fig2, use_container_width=True)

    highlights = sent_data.get('highlights', {})
    hc1, hc2 = st.columns(2)
    with hc1:
        if highlights.get('most_positive'):
            st.success(f"**Most Positive Moment**\n\n\"{highlights['most_positive']['text_preview']}\"")
    with hc2:
        if highlights.get('most_negative'):
            st.error(f"**Most Negative/Heated Moment**\n\n\"{highlights['most_negative']['text_preview']}\"")

st.divider()

st.markdown("### Detailed Stats")
stat_df = pd.DataFrame({
    "Metric": ["Unique Words", "Vocabulary Richness", "Avg Sentence Length", "Reading Time"],
    "Value": [stats.get('unique_words', 0), f"{stats.get('vocabulary_richness', 0):.2f}", f"{stats.get('avg_sentence_length', 0):.1f} words", f"{stats.get('reading_time_min', 0)} mins"]
})
st.dataframe(stat_df, hide_index=True, use_container_width=True)
