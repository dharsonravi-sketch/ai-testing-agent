import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_response(system_prompt: str, user_message: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,
        max_completion_tokens=2048
    )
    return response.choices[0].message.content

def get_response_with_rag(system_prompt: str, user_message: str, past_patterns: list) -> str:
    rag_context = ""

    if past_patterns:
        rag_context = "\n\nHere are similar past test patterns:\n"
        for i, pattern in enumerate(past_patterns, start=1):
            rag_context += f"\n--- Pattern {i} ---\n"
            rag_context += f"Tests:\n{pattern.get('tests', '')[:500]}\n"
            rag_context += f"Analysis:\n{pattern.get('analysis', '')[:300]}\n"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message + rag_context}
        ],
        temperature=0.2,
        max_completion_tokens=2048
    )
    return response.choices[0].message.content