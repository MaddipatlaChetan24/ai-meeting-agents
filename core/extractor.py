#Actionableitems , decision , questions 

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os 
import json

def get_llm():
    return ChatMistralAI(model = "mistral-small-latest", mistral_api_key = os.getenv("MISTRAL_API_KEY"),temperature=0.2)

def build_chain(system_prompt : str):
    llm = get_llm()
    return (
        RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) |ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human","{text}"),
    ]) | llm |StrOutputParser()
    )

def chunk_transcript_for_extraction(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    return splitter.split_text(transcript)

def extract_action_items(transcript:str)->str:
    """Extract action items from transcript, handling chunking for long texts."""
    chain = build_chain(
         "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. Return the result as a JSON array of objects. "
        "Each object must have the following string keys: "
        "'task' (Task description), "
        "'owner' (who is responsible), "
        "'deadline' (if mentioned, else 'Not specified'), "
        "'priority' (High, Medium, or Low). "
        "If no action items are found, return an empty JSON array: []. "
        "Return ONLY the raw JSON array, with no markdown formatting or text."
    )

    chunks = chunk_transcript_for_extraction(transcript)
    all_items = []
    
    for chunk in chunks:
        res = chain.invoke(chunk)
        try:
            # Clean up potential markdown formatting from LLM
            clean_res = res.replace("```json", "").replace("```", "").strip()
            items = json.loads(clean_res)
            if isinstance(items, list):
                all_items.extend(items)
        except json.JSONDecodeError:
            pass # Ignore malformed JSON chunks
            
    return json.dumps(all_items, indent=2)

def extract_key_decisions(transcript: str) -> str:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
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