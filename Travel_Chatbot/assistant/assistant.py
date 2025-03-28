import uuid
from typing import Dict, List, Any, Optional, Generator, Set, Tuple

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver

import config
from assistant.graph import create_assistant_graph
from database.connection import reset_database


class TravelAssistant:
    """
    Main travel assistant implementation that manages conversation state.
    """
    def __init__(self, passenger_id: Optional[str] = None):
        """
        Initialize the travel assistant.
        
        Args:
            passenger_id: ID of the passenger (user)
        """
        self.passenger_id = passenger_id or config.DEFAULT_PASSENGER_ID
        self.thread_id = str(uuid.uuid4())
        self.graph = create_assistant_graph()
        self._printed_messages: Set[str] = set()
        
        # Reset the database to ensure it's in a clean state
        reset_database()
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration for the graph.
        
        Returns:
            Configuration dictionary
        """
        return {
            "configurable": {
                "passenger_id": self.passenger_id,
                "thread_id": self.thread_id,
            }
        }
    
    def chat(self, message: str) -> Generator[Dict[str, Any], None, None]:
        """
        Send a message to the assistant and yield responses.
        
        Args:
            message: User message
            
        Yields:
            Response events from the assistant
        """
        config = self.get_config()
        events = self.graph.stream(
            {"messages": ("user", message)}, config, stream_mode="values"
        )
        
        for event in events:
            print(f"DEBUG: Got event: {event.keys()}")
            if event.get('dialog_state'):
                print(f"DEBUG: Dialog state: {event.get('dialog_state')}")
            
            yield event
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the conversation.
        
        Returns:
            Current state
        """
        return self.graph.get_state(self.get_config())
    
    def needs_approval(self) -> bool:
        """
        Check if the assistant is waiting for approval.
        
        Returns:
            True if approval is needed, False otherwise
        """
        try:
            snapshot = self.get_state()
            needs_approval = bool(snapshot.next)
            if needs_approval:
                print(f"DEBUG: Assistant needs approval. Next node: {snapshot.next}")
            return needs_approval
        except Exception as e:
            print(f"DEBUG: Error checking if approval is needed: {e}")
            return False
    
    def approve(self) -> List[Dict[str, Any]]:
        """
        Approve the pending action.
        
        Returns:
            List of events resulting from the approval
        """
        try:
            if not self.needs_approval():
                print("DEBUG: No approval needed in approve")
                return []
            
            # Check if we have a next node
            snapshot = self.get_state()
            if not snapshot.next:
                print("DEBUG: No next node in state")
                return []
                
            print(f"DEBUG: Approving action, next node: {snapshot.next}")
            
            config = self.get_config()
            result = self.graph.invoke(None, config)
            
            print(f"DEBUG: Got result from graph.invoke: {result.keys()}")
            
            if "messages" in result:
                print(f"DEBUG: Got {len(result['messages'])} messages in result")
                
            # Clear the saved tool call after approval
            if "last_tool_call" in self._custom_data:
                del self._custom_data["last_tool_call"]
                
            return result.get("messages", [])
            
        except Exception as e:
            print(f"DEBUG: Error in approve: {e}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def reject(self, reason: str) -> List[Dict[str, Any]]:
        """
        Reject the pending action with a reason.
        
        Args:
            reason: Reason for rejection
            
        Returns:
            List of events resulting from the rejection
        """
        try:
            if not self.needs_approval():
                print("DEBUG: No approval needed in reject")
                return []
            
            snapshot = self.get_state()
            print(f"DEBUG: Got state in reject, next = {snapshot.next}")
            
            # Try to get tool call from snapshot
            tool_call_id = None
            
            if hasattr(snapshot, 'messages') and snapshot.messages:
                last_message = snapshot.messages[-1]
                
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    tool_call_id = last_message.tool_calls[0]["id"]
                    print(f"DEBUG: Found tool call ID in snapshot: {tool_call_id}")
            
            # If we don't have a tool call ID but we have one in session state, use that
            if not tool_call_id and "last_tool_call" in self._printed:
                tool_call_id = self._printed["last_tool_call"]["id"]
                print(f"DEBUG: Using tool call ID from session state: {tool_call_id}")
            
            # If we still don't have a tool call ID, generate a fake one
            if not tool_call_id:
                tool_call_id = "unknown_tool_call_id"
                print("DEBUG: Using fake tool call ID")
            
            config = self.get_config()
            result = self.graph.invoke(
                {
                    "messages": [
                        ToolMessage(
                            tool_call_id=tool_call_id,
                            content=f"API call denied by user. Reasoning: '{reason}'. Continue assisting, accounting for the user's input.",
                        )
                    ]
                },
                config,
            )
            
            print(f"DEBUG: Got result from graph.invoke: {result.keys()}")
            
            if "messages" in result:
                print(f"DEBUG: Got {len(result['messages'])} messages in result")
            
            return result.get("messages", [])
            
        except Exception as e:
            print(f"DEBUG: Error in reject: {e}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def get_pending_action(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Get details about the pending action that needs approval.
        
        Returns:
            Tuple of (tool_name, arguments) or None if no action is pending
        """
        try:
            # First check if the last message has tool calls
            snapshot = self.get_state()
            
            if hasattr(snapshot, 'messages') and snapshot.messages:
                last_message = snapshot.messages[-1]
                
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    tool_call = last_message.tool_calls[0]
                    print(f"DEBUG: Found tool call in get_pending_action: {tool_call['name']}")
                    return (tool_call["name"], tool_call["args"])
            
            # If no tool call found but we need approval, something is wrong
            if self.needs_approval():
                print("DEBUG: Assistant needs approval but no tool call found")
                return None
                
            print("DEBUG: No approval needed in get_pending_action")
            return None
            
        except Exception as e:
            print(f"DEBUG: Error in get_pending_action: {e}")
            return None