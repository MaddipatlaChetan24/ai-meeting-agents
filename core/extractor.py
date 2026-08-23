#Actionableitems , decision , questions 

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os 
impo_for_extraction(transcript)
    all_items = []
    
    for chunk in chunks:
        res = chain.invoke(chunk)
        try:und.'"
    )
    # Simple chunking logic to avoid context window limit
    chunks = chunk_transcript_for_extraction(transcript)
    results = [chain.invoke(chunk) for chunk in chunks]
    
    # Combine results
    combined = "\n\n".join(r for r in results if r.strip() and "no key decisions found" not in r.lower())
    if not combined.strip():
        return "No key decisions found."
    return combined

def extract_questions(transcript: str) -> str:
    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    chunks = chunk_transcript_for_extraction(transcript)
    results = [chain.invoke(chunk) for chunk in chunks]
    
    combined = "\n\n".join(r for r in results if r.strip() and "no open questions found" not in r.lower())
    if not combined.strip():
        return "No open questions found."
    return combined
