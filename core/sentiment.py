from textblob import TextBlob
import re

def analyze_sentiment(transcript: str, chunk_size: int = 500) -> dict:
    """
    Analyze sentiment across the meeting transcript.
    
    Returns dict with:
    - 'overall': {'polarity': float, 'subjectivity': float, 'label': str, 'emoji': str}
    - 'timeline': [{'chunk_index': int, 'text_preview': str, 'polarity': float, 'subjectivity': float, 'label': str}]
    - 'highlights': {'most_positive': dict, 'most_negative': dict}
    """
    if not transcript or not transcript.strip():
        return {
            'overall': {'polarity': 0.0, 'subjectivity': 0.0, 'label': 'Neutral', 'emoji': '😐'},
            'timeline': [],
            'highlights': {'most_positive': None, 'most_negative': None}
        }

    # Split into chunks (approx words, but character-based for simplicity)
    chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
    
    timeline = []
    total_polarity = 0
    total_subjectivity = 0
    
    most_positive = None
    most_negative = None

    for i, chunk in enumerate(chunks):
        blob = TextBlob(chunk)
        pol = blob.sentiment.polarity
        subj = blob.sentiment.subjectivity
        
        # Labeling
        if pol > 0.5:
            label = "Excellent"
        elif pol > 0.1:
            label = "Positive"
        elif pol < -0.5:
            label = "Heated"
        elif pol < -0.1:
            label = "Negative"
        else:
            label = "Neutral"

        chunk_data = {
            'chunk_index': i + 1,
            'text_preview': chunk[:80].replace('\n', ' ') + "...",
            'polarity': pol,
            'subjectivity': subj,
            'label': label
        }
        timeline.append(chunk_data)
        
        total_polarity += pol
        total_subjectivity += subj
        
        if most_positive is None or pol > most_positive['polarity']:
            most_positive = chunk_data
        if most_negative is None or pol < most_negative['polarity']:
            most_negative = chunk_data

    num_chunks = len(chunks)
    avg_polarity = total_polarity / num_chunks
    avg_subjectivity = total_subjectivity / num_chunks
    
    # Overall Label
    if avg_polarity > 0.1:
        overall_label = "Positive"
        emoji = "😊"
    elif avg_polarity < -0.1:
        overall_label = "Negative"
        emoji = "😟"
    else:
        overall_label = "Neutral"
        emoji = "😐"

    if most_positive and most_positive['polarity'] <= 0.1:
        most_positive = None
    if most_negative and most_negative['polarity'] >= -0.1:
        most_negative = None

    return {
        'overall': {
            'polarity': avg_polarity,
            'subjectivity': avg_subjectivity,
            'label': overall_label,
            'emoji': emoji
        },
        'timeline': timeline,
        'highlights': {
            'most_positive': most_positive,
            'most_negative': most_negative
        }
    }
