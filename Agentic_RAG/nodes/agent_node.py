import logging
from langchain_openai import ChatOpenAI
from core.config import AGENT_MODEL

logger = logging.getLogger(__name__)

def agent(state):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply end.

    Args:
        state (messages): The current state containing messages

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    logger.info("Executing agent node")
    messages = state["messages"]
    
    # Get tools from state if available, otherwise use empty list
    tools = state["tools"]
    
    # Create ChatOpenAI model
    model = ChatOpenAI(
        temperature=0, 
        streaming=True, 
        model=AGENT_MODEL
    )
    
    # Bind tools if available
    if tools:
        model = model.bind_tools(tools)
    
    # Invoke model
    response = model.invoke(messages)
    
    logger.info(f"Agent response: {response.content[:100]}...")
    
    # Return response as a list to be added to the existing list
    return {"messages": [response]}