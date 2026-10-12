import os

from dotenv import load_dotenv

load_dotenv()

for name in ["LANGSMITH_TRACING", "LANGSMITH_PROJECT", "LANGSMITH_ENDPOINT", "LANGCHAIN_TRACING_V2"]:
    print(f"{name} = {os.getenv(name)}")

key = os.getenv("LANGSMITH_API_KEY")
print("LANGSMITH_API_KEY set:", bool(key), "| starts with:", (key or "")[:6])

from langsmith import Client, utils

print("tracing enabled:", utils.tracing_is_enabled())

try:
    projects = list(Client().list_projects(limit=3))
    print("connection OK, projects:", [p.name for p in projects])
except Exception as exc:
    print("connection FAILED:", exc)