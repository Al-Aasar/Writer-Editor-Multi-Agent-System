from langchain_groq import ChatGroq
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")

model = "qwen/qwen3.8-27b"

llm_groq = ChatGroq(
    model=model,
    api_key=GROQ_API_KEY,
    temperature=0.0,
)