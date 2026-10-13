import os
from langchain_google_genai import ChatGoogleGenerativeAI

api_key = os.environ.get("GEMINI_API_KEY")
model = "gemini-3-flash-preview"

llm_gemini = ChatGoogleGenerativeAI(
    model=model,
    google_api_key=api_key,
    temperature=0.0,
    thinking_level="low",
)