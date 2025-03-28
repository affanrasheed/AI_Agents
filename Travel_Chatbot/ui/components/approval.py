"""
Approval interface component for the Travel Assistant UI.
"""
import os
import sys
import json
from typing import Dict, Any

import streamlit as st

# Add the parent directory to the path so we can import from other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# No direct imports from assistant.assistant or ui.components.chat to avoid circular imports


class ApprovalInterface:
    """
    Interface for approving or rejecting assistant actions.
    """
    def __init__(self):
        """Initialize the approval interface."""
        # Initialize rejection reason if not in session state
        if "rejection_reason" not in st.session_state:
            st.session_state.rejection_reason = ""
    
    def _get_tool_description(self, tool_name: str) -> str:
        """
        Get a user-friendly description of a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            User-friendly description
        """
        descriptions = {
            "update_ticket_to_new_flight": "Update your flight booking",
            "cancel_ticket": "Cancel your flight booking",
            "book_car_rental": "Book a car rental",
            "update_car_rental": "Update your car rental booking",
            "cancel_car_rental": "Cancel your car rental",
            "book_hotel": "Book a hotel",
            "update_hotel": "Update your hotel booking",
            "cancel_hotel": "Cancel your hotel booking",
            "book_excursion": "Book an excursion",
            "update_excursion": "Update your excursion booking",
            "cancel_excursion": "Cancel your excursion"
        }
        return descriptions.get(tool_name, tool_name.replace("_", " ").title())
    
    def _handle_approve(self):
        """Handle approval of the pending action."""
        try:
            assistant = st.session_state.assistant
            
            with st.spinner("Processing..."):
                print("DEBUG: Processing approval")
                # Approve the action
                messages = assistant.approve()
                
                print(f"DEBUG: Got {len(messages)} messages after approval")
                # Add the assistant's response to chat history
                if messages and hasattr(messages[-1], "content") and messages[-1].content:
                    content = messages[-1].content
                    print(f"DEBUG: Adding response to history: {content[:50]}...")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": content
                    })
                else:
                    print("DEBUG: No content in messages after approval")
            
            # Reset pending approval
            st.session_state.pending_approval = False
            
            # Clear saved tool call
            if "last_tool_call" in st.session_state:
                del st.session_state.last_tool_call
            
            # Force a rerun to update the UI
            st.rerun()
        except Exception as e:
            st.error(f"Error during approval: {str(e)}")
            print(f"ERROR: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _handle_reject(self):
        """Handle rejection of the pending action."""
        try:
            assistant = st.session_state.assistant
            reason = st.session_state.rejection_reason
            
            if not reason.strip():
                st.error("Please provide a reason for rejection.")
                return
            
            with st.spinner("Processing..."):
                print(f"DEBUG: Processing rejection with reason: {reason}")
                
                # Get the tool call ID from session state
                tool_call_id = None
                if "last_tool_call" in st.session_state:
                    tool_call_id = st.session_state.last_tool_call.get("id")
                
                # Reject the action
                messages = []
                if tool_call_id:
                    # Use the reject function with the tool call ID
                    messages = assistant.reject(reason)
                else:
                    # Add a manual rejection message if we don't have a tool call ID
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"I understand you don't want to proceed with this action. Let me know if there's anything else I can help with."
                    })
                
                # Add the assistant's response to chat history
                if messages and hasattr(messages[-1], "content") and messages[-1].content:
                    content = messages[-1].content
                    print(f"DEBUG: Adding response to history: {content[:50]}...")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": content
                    })
                else:
                    print("DEBUG: No content in messages after rejection")
            
            # Reset pending approval and rejection reason
            st.session_state.pending_approval = False
            st.session_state.rejection_reason = ""
            
            # Reset rejection container
            if "rejection_container" in st.session_state:
                st.session_state.rejection_container = False
            
            # Clear saved tool call
            if "last_tool_call" in st.session_state:
                del st.session_state.last_tool_call
            
            # Force a rerun to update the UI
            st.rerun()
        except Exception as e:
            st.error(f"Error during rejection: {str(e)}")
            print(f"ERROR: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def render(self, tool_name: str, args: Dict[str, Any]):
        """
        Render the approval interface.
        
        Args:
            tool_name: Name of the tool to be executed
            args: Arguments for the tool
        """
        # Add a highly visible warning for the approval
        st.warning("⚠️ **Action Requires Your Approval**")
        
        # Add a distinctive background for the approval interface
        st.markdown("""
        <style>
        .approval-container {
            background-color: #fffaeb;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .tool-header {
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .tool-args {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="approval-container">', unsafe_allow_html=True)
        
        # Show a friendly description of what's happening
        st.markdown(f"The assistant wants to **{self._get_tool_description(tool_name)}**")
        
        # Format the arguments
        args_json = json.dumps(args, indent=2)
        st.markdown(f'<div class="tool-args">{args_json}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Use columns for the approve/reject buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Approve", key="approve_button", type="primary", use_container_width=True):
                self._handle_approve()
        
        with col2:
            if st.button("❌ Reject", key="reject_button", use_container_width=True):
                if "rejection_container" not in st.session_state:
                    st.session_state.rejection_container = True
        
        # Show rejection reason input if reject button was clicked
        if st.session_state.get("rejection_container", False):
            st.text_area(
                "Reason for rejection",
                key="rejection_reason",
                placeholder="Please explain why you're rejecting this action...",
                height=100
            )
            
            if st.button("Submit Rejection", key="submit_rejection", type="primary"):
                self._handle_reject()