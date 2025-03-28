"""
Sidebar component for the Travel Assistant UI.
"""
import os
import sys
import streamlit as st

# Add the parent directory to the path so we can import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import config


def setup_sidebar():
    """Set up the sidebar with configuration options."""
    with st.sidebar:
        st.title("Settings")
        
        # Passenger ID input
        st.subheader("Passenger Information")
        passenger_id = st.text_input(
            "Passenger ID",
            value=st.session_state.passenger_id,
            help="Enter your passenger ID to access your flight information."
        )
        
        # Update passenger ID if changed
        if passenger_id != st.session_state.passenger_id:
            st.session_state.passenger_id = passenger_id
            
            # Reset assistant with new passenger ID if we already have one
            if "assistant" in st.session_state:
                st.session_state.assistant = None
                st.session_state.messages = []
                st.session_state.pending_approval = False
                st.rerun()
        
        # Add information about the assistant
        st.subheader("About")
        st.markdown("""
        This travel assistant helps you manage your Swiss Airlines bookings and travel plans.
        
        You can:
        - Check your flight information
        - Change or cancel flights
        - Book hotels and car rentals
        - Find and book excursions
        
        For sensitive operations that modify your bookings, the assistant will ask for your approval.
        """)
        
        # Debug section (collapsible)
        with st.expander("Debug Information", expanded=False):
            st.subheader("Session State")
            st.write("Pending approval:", st.session_state.get("pending_approval", False))
            
            if "assistant" in st.session_state and st.session_state.assistant:
                assistant = st.session_state.assistant
                st.write("Thread ID:", assistant.thread_id)
                
                # Add button to check state
                if st.button("Check Assistant State"):
                    try:
                        state = assistant.get_state()
                        st.json({
                            "next": str(state.next) if hasattr(state, "next") else None,
                            "has_messages": bool(state.messages) if hasattr(state, "messages") else False,
                            "message_count": len(state.messages) if hasattr(state, "messages") and state.messages else 0
                        })
                    except Exception as e:
                        st.error(f"Error getting state: {str(e)}")
            
            # Reset button
            if st.button("Reset Application State"):
                for key in list(st.session_state.keys()):
                    if key != "initialized":
                        del st.session_state[key]
                st.session_state.messages = []
                st.session_state.passenger_id = config.DEFAULT_PASSENGER_ID
                st.session_state.pending_approval = False
                st.rerun()