import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import io

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 
    'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 
    'will', 'would', 'could', 'sho

def clean_text(text: str) -> list:
    """Lowercase and remove punctuation, return list of words."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.split()

def generate_word_cloud(transcript: str) -> bytes:
    """
    Generate a word cloud image from the transcript.
    Returns PNG image as bytes.
    Uses dark theme colors matching the app's gradient.
    """
    if not transcript or not transcript.strip():
        return b""

    # Custom colormap using the app's brand colors
    # #3B82F6 (blue), #8B5CF6 (purple), #EC4899 (pink), #06B6D4 (cyan)
    colors = ["#3B82F6", "#06B6D4", "#8B5CF6", "#EC4899", "#A855F7"]
    cmap = LinearSegmentedColormap.from_list("BrandColors", colors)

    wc = WordCloud(
        width=800, 
        height=400,
        background_color="#0E1117", # App dark background
        colormap=cmap,
        stopwords=STOPWORDS,
        max_words=100,
        contour_width=0,
        prefer_horizontal=0.9
    )
    
    wc.generate(transcript)
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    image = wc.to_image()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def get_keyword_frequency(transcript: str, top_n: int = 15) -> list:
    """
    Get top keywords by frequency.
    Returns: [{'word': str, 'count': int}]
    """
    words = clean_text(transcript)
    filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    
    counter = Counter(filtered_words)
    top_words = counter.most_common(top_n)
    
    return [{'word': word, 'count': count} for word, count in top_words]

def get_meeting_stats(transcript: str) -> dict:
    """
    Calculate meeting statistics.
    """
    words = clean_text(transcript)
    total_words = len(words)
    unique_words = len(set(words))
    
    # Simple sentence split based on punctuation
    sentences = re.split(r'[.!?]+', transcript)
    total_sentences = len([s for s in sentences if s.strip()])
    
    avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
    vocabulary_richness = unique_words / total_words if total_words > 0 else 0
    
    # Approx 150 words per minute speaking
    estimated_duration_min = max(1, total_words // 150)
    # Approx 200 words per minute reading
    reading_time_min = max(1, total_words // 200)

    return {
        'total_words': total_words,
        'unique_words': unique_words,
        'vocabulary_richness': vocabulary_richness,
        'avg_sentence_length': avg_sentence_length,
        'estimated_duration_min': estimated_duration_min,
        'total_sentences': total_sentences,
        'reading_time_min': reading_time_min
    }
