"""
Assistant models and state definitions.
"""
from typing import Dict, List, Any, TypedDict, Annotated

from langchain_core.messages import ToolMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph.message import AnyMessage, add_messages


class State(TypedDict):
    """
    State for the travel assistant graph.
    """
    messages: Annotated[List[AnyMessage], add_messages]
    user_info: Dict[str, Any]


class Assistant:
    """
    Assistant class that wraps a runnable LLM.
    """
    def __init__(self, runnable: Runnable):
        """
        Initialize the assistant with a runnable LLM.
        
        Args:
            runnable: A runnable LLM instance
        """
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig) -> Dict[str, Any]:
        """
        Process the current state and generate a response.
        
        Args:
            state: The current state
            config: Configuration for the runnable
            
        Returns:
            Updated state with assistant's response
        """
        while True:
            result = self.runnable.invoke(state, config)
            # If the LLM happens to return an empty response, re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, List)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


def handle_tool_error(state: Dict[str, Any]) -> Dict[str, List[ToolMessage]]:
    """
    Handle errors from tool execution.
    
    Args:
        state: The current state with an error
        
    Returns:
        Updated state with error message
    """
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }