import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from core.config import REWRITE_MODEL

logger = logging.getLogger(__name__)

def rewrite(state):
    """
    Transform the query to produce a better question when documents aren't relevant.

    Args:
        state (messages): The current state containing messages

    Returns:
        dict: The updated state with re-phrased question
    """
    logger.info("Rewriting query for better retrieval")
    
    # Get messages and extract question
    messages = state["messages"]
    question = messages[0].content
    
    # Create message for rewriting
    msg = [
        HumanMessage(
            content=f""" \n 
    Look at the input and try to reason about the underlying semantic intent / meaning. \n 
    Here is the initial question:
    \n ------- \n
    {question} 
    \n ------- \n
    Formulate an improved question: """,
        )
    ]
    
    # Create ChatOpenAI model
    model = ChatOpenAI(
        temperature=0, 
        model=REWRITE_MODEL, 
        streaming=True
    )
    
    # Invoke model
    response = model.invoke(msg)
    
    logger.info(f"Rewritten query: {response.content[:100]}...")
    
    # Return response
    return {"messages": [response]}