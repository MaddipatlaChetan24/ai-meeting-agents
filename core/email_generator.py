 A clear closing and professional sign-off
         
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
        return f"Subject: Follow-up: {title}\n\nCould n
        return chain.invoke({
            "title": title,
            "summary": summary,
            "actions": actions,
            "decisions": decisions
        })
    except Exception as e:
        print(f"Error generating email: {e}")
        return f"Subject: Follow-up: {title}\n\nCould not generate email due
