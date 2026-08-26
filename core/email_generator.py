 A clear closing and professional sign-off
         
         Return ONLY the email text. Do not include introductory or explanatory text.
         """),
        ("human", 
         "Title: {title}\n\nSummary: {summary}\n\nAction Items:\n{actions}\n\nDecisions:\n{decisions}")
    ])

        print(f"Error generating email: {e}")
        return f"Subject: Follow-up: {title}\n\nCould not generate email due
