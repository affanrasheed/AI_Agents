"""
State graph definition for the Travel Assistant.
"""
from typing import Dict, List, Any, Set, Literal

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition, ToolNode

import config
from assistant.models import State, Assistant, handle_tool_error
from assistant.prompts import assistant_prompt
from tools.car_tools import (
    search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
)
from tools.flight_tools import (
    fetch_user_flight_information, search_flights, 
    update_ticket_to_new_flight, cancel_ticket
)
from tools.hotel_tools import (
    search_hotels, book_hotel, update_hotel, cancel_hotel
)
from tools.policy_tools import lookup_policy
from tools.recommendation_tools import (
    search_trip_recommendations, book_excursion, 
    update_excursion, cancel_excursion
)


# Define safe tools (read-only operations)
SAFE_TOOLS = [
    TavilySearchResults(max_results=1),
    fetch_user_flight_information,
    search_flights,
    lookup_policy,
    search_car_rentals,
    search_hotels,
    search_trip_recommendations,
]

# Define sensitive tools (operations that require user confirmation)
SENSITIVE_TOOLS = [
    update_ticket_to_new_flight,
    cancel_ticket,
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
    book_hotel,
    update_hotel,
    cancel_hotel,
    book_excursion,
    update_excursion,
    cancel_excursion,
]

# Get the set of sensitive tool names for routing
SENSITIVE_TOOL_NAMES: Set[str] = {t.name for t in SENSITIVE_TOOLS}


def create_tool_node_with_fallback(tools: List[Any]) -> ToolNode:
    """
    Create a tool node with error handling.
    
    Args:
        tools: List of tools to include in the node
        
    Returns:
        Tool node with error handling
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def create_assistant_graph() -> StateGraph:
    """
    Create the state graph for the assistant.
    
    Returns:
        Compiled state graph
    """
    # Initialize the LLM
    llm = ChatAnthropic(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
    )
    
    # Create the assistant runnable with all tools
    assistant_runnable = assistant_prompt | llm.bind_tools(SAFE_TOOLS + SENSITIVE_TOOLS)
    
    # Build the graph
    builder = StateGraph(State)
    
    # Add nodes to the graph
    builder.add_node("fetch_user_info", lambda state: {"user_info": fetch_user_flight_information.invoke({})})
    builder.add_node("assistant", Assistant(assistant_runnable))
    builder.add_node("safe_tools", create_tool_node_with_fallback(SAFE_TOOLS))
    builder.add_node("sensitive_tools", create_tool_node_with_fallback(SENSITIVE_TOOLS))
    
    # Define edges
    builder.add_edge(START, "fetch_user_info")
    builder.add_edge("fetch_user_info", "assistant")
    
    # Define conditional routing logic
    def route_tools(state: State) -> Literal["safe_tools", "sensitive_tools", "END"]:
        """Route to the appropriate tools based on the assistant's response."""
        next_node = tools_condition(state)
        # If no tools are invoked, return to the user
        if next_node == END:
            return END
            
        ai_message = state["messages"][-1]
        # This assumes single tool calls. For parallel tool calling,
        # you'd want to use an ANY condition
        first_tool_call = ai_message.tool_calls[0]
        if first_tool_call["name"] in SENSITIVE_TOOL_NAMES:
            return "sensitive_tools"
        return "safe_tools"
    
    # Add conditional edges
    builder.add_conditional_edges(
        "assistant", route_tools, ["safe_tools", "sensitive_tools", END]
    )
    
    # Complete the graph
    builder.add_edge("safe_tools", "assistant")
    builder.add_edge("sensitive_tools", "assistant")
    
    # Compile the graph with interruption before sensitive tools
    memory = MemorySaver()
    graph = builder.compile(
        checkpointer=memory,
        # The graph will always halt before executing sensitive tools.
        # The user can approve or reject before the assistant continues
        interrupt_before=["sensitive_tools"],
    )
    
    return graph