from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage


class WriterState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str

    # Guardrails
    guardrail_allowed: bool
    guardrail_reason: str
    guardrail_category: str     

    draft: str                   
    feedback: str               
    editor_approved: bool        
    iteration: int               
    research: str
    
    # Output
    final_response: str          
    error: str                   
    llm_calls: int