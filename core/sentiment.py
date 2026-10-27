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
        subj = blob.sentiment.subjectivity
        
        total_polarity += pol
        total_subjectivity += subj
        
        if most_positive is None or pol > most_positive['polarity']:
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
