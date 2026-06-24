import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_llm():
    return ChatMistralAI(model='mistral-small-latest', temperature=0.4)

def generate_follow_up_email(title: str, summary: str, actions: str, decisions: str) -> str:
    """
    Generate a professional follow-up email based on meeting results.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         """You are an executive assistant writing a professional follow-up email.
         
         Use the provided meeting details to draft an email that includes:
         - A professional subject line based on the meeting title
         - A polite greeting
         - A brief recap of the meeting (2-3 sentences based on the summary)
         - Action items clearly formatted with owners
         - Key decisions if any were made
         - A clear closing and professional sign-off
         
         Return ONLY the email text. Do not include introductory or explanatory text.
         """),
        ("human", 
         "Title: {title}\n\nSummary: {summary}\n\nAction Items:\n{actions}\n\nDecisions:\n{decisions}")
    ])
    
    llm = get_llm()
    chain = prompt | llm | StrOutputParser()
    
    try:
        return chain.invoke({
            "title": title,
            "summary": summary,
            "actions": actions,
            "decisions": decisions
        })
    except Exception as e:
        print(f"Error generating email: {e}")
        return f"Subject: Follow-up: {title}\n\nCould not generate email due to an error."
