from groq import Groq
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def parse_complaint(complaint_text, location):
    prompt = f"""
    Analyze this civic complaint and return ONLY a JSON object, nothing else.
    
    Complaint: {complaint_text}
    Location: {location}
    
    Return this exact JSON format:
    {{
        "category": "Road/Water/Electricity/Sanitation/Other",
        "severity": "Low/Medium/High/Critical",
        "urgency": "Low/Medium/High",
        "affected_population": "Small/Medium/Large",
        "risk_level": "Low/Medium/High/Critical",
        "priority_score": 75,
        "summary": "one line summary here",
        "estimated_resolution_days": 3
    }}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    text = response.choices[0].message.content.strip()
    
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return json.loads(text)