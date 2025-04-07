from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    State definition for the RAG agent workflow.
    
    The add_messages function defines how an update should be processed.
    Default is to replace. add_messages says "append"
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tools: list  # List of tools available to the agent

# Additional state classes can be defined here if needed for UI state management
class UIState:
    """State management for the UI layer"""
    def __init__(self):
        self.current_step = None  # Current step in the workflow
        self.processing = False   # Whether processing is ongoing
        self.history = []         # Chat history
        self.debug_info = []      # Debug information for each step
        
    def add_message(self, role, content):
        """Add a message to the chat history"""
        self.history.append({"role": role, "content": content})
        
    def add_debug_info(self, step, content):
        """Add debug information for a step"""
        self.debug_info.append({"step": step, "content": content})
        
    def clear_history(self):
        """Clear the chat history"""
        self.history = []
        self.debug_info = []
        
    def set_processing(self, processing):
        """Set the processing state"""
        self.processing = processing
        
    def set_current_step(self, step):
        """Set the current step"""
        self.current_step = step