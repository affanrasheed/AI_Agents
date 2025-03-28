"""
Chat interface component for the Travel Assistant UI.
"""
import os
import sys
import json
from typing import Dict, Any, Optional

import streamlit as st
from assistant.graph import SENSITIVE_TOOL_NAMES

# Add the parent directory to the path so we can import from other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the approval interface first to avoid circular imports
from ui.components.approval import ApprovalInterface

# Now import the assistant
from assistant.assistant import TravelAssistant
from assistant.graph import SENSITIVE_TOOL_NAMES


class ChatInterface:
    """
    Chat interface component for interacting with the assistant.
    """
    def __init__(self):
        """Initialize the chat interface."""
        # Initialize the assistant if not already in session state
        if "assistant" not in st.session_state:
            st.session_state.assistant = TravelAssistant(
                passenger_id=st.session_state.passenger_id
            )
        
        # Initialize approval interface
        self.approval_interface = ApprovalInterface()
    
    def _initialize_chat(self):
        """Initialize or reset the chat interface."""
        st.session_state.messages = []
        st.session_state.pending_approval = False
        st.session_state.assistant = TravelAssistant(
            passenger_id=st.session_state.passenger_id
        )
    
    def _handle_message_submit(self, message: str):
        """
        Handle submission of a new message.
        
        Args:
            message: User message
        """
        if not message.strip():
            return
            
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": message})
        
        # Get assistant response
        assistant = st.session_state.assistant
        
        last_message = None
        with st.spinner("Thinking..."):
            # Process the message through the assistant
            for event in assistant.chat(message):
                # Skip empty events
                if not event.get("messages"):
                    continue
                    
                # Add the assistant's response to chat history
                message_event = event["messages"][-1]
                last_message = message_event
                
                if hasattr(message_event, "content") and message_event.content:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": message_event.content
                    })
        
        # Check if we need approval by first checking the message for tool_calls
        needs_approval = False
        
        # Check for tool calls in the last message
        if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_name = last_message.tool_calls[0]["name"]
            # Store tool call in session state instead of in the assistant
            st.session_state.last_tool_call = last_message.tool_calls[0]
            
            # Check if the tool is a sensitive tool
            
            if tool_name in SENSITIVE_TOOL_NAMES:
                needs_approval = True
                print(f"DEBUG: Detected sensitive tool call: {tool_name}")
        
        # Also check the assistant state
        if assistant.needs_approval():
            needs_approval = True
            print("DEBUG: Assistant needs approval based on state check")
        
        if needs_approval:
            st.session_state.pending_approval = True
            print("DEBUG: Setting pending_approval = True")
        
        # Force a rerun to update the UI
        st.rerun()
    
    def _format_arguments(self, args: Dict[str, Any]) -> str:
        """
        Format tool arguments for display.
        
        Args:
            args: Tool arguments dictionary
            
        Returns:
            Formatted arguments string
        """
        return json.dumps(args, indent=2)
    
    def _display_messages(self):
        """Display the chat message history."""
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                st.markdown(f'<div class="user-message"><strong>You:</strong> {content}</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message"><strong>Assistant:</strong> {content}</div>', 
                           unsafe_allow_html=True)
    
    def _display_pending_approval(self):
        """Display the pending approval interface if needed."""
        if not st.session_state.get("pending_approval", False):
            print("DEBUG: pending_approval is False, not displaying approval interface")
            return
            
        print("DEBUG: pending_approval is True, trying to display approval interface")
        
        # First try to get the action from the assistant
        assistant = st.session_state.assistant
        pending_action = assistant.get_pending_action()
        
        # If that fails, try to use the saved tool call from session state
        if not pending_action and "last_tool_call" in st.session_state:
            tool_call = st.session_state.last_tool_call
            pending_action = (tool_call["name"], tool_call["args"])
            print(f"DEBUG: Using saved tool call from session state: {tool_call['name']}")
        
        # Display the approval interface if we have a pending action
        if pending_action:
            print(f"DEBUG: Got pending action: {pending_action[0]}")
            tool_name, args = pending_action
            self.approval_interface.render(tool_name, args)
        else:
            print("DEBUG: No pending action found despite pending_approval=True")
            # If there's no pending action but the flag is set, reset it
            st.session_state.pending_approval = False
            # Show a message that the state has been reset
            st.info("The pending approval state has been reset. You can continue the conversation.")
            st.rerun()
    
    def render(self):
        """Render the chat interface."""
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Button to reset chat
            if st.button("New Conversation"):
                self._initialize_chat()
                st.rerun()
            
            # Display chat messages
            self._display_messages()
            
            # Display pending approval alert if needed
            if st.session_state.get("pending_approval", False):
                st.warning("⚠️ **Action Requires Your Approval**. Please review and approve or reject the action below.")
            
            # Display pending approval interface if needed
            self._display_pending_approval()
            
            # Message input - disabled if waiting for approval
            user_input = st.chat_input(
                "Type your message here...", 
                disabled=st.session_state.get("pending_approval", False)
            )
            
            if user_input:
                self._handle_message_submit(user_input)