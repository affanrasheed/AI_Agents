"""
Main Streamlit application for the Travel Assistant.
"""
import os
import sys
import streamlit as st

# Add the parent directory to the path so we can import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from ui.components.chat import ChatInterface
from ui.components.sidebar import setup_sidebar


def setup_page():
    """Set up the Streamlit page configuration."""
    st.set_page_config(
        page_title=config.UI_TITLE,
        page_icon=config.UI_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Set page header
    st.title(f"{config.UI_ICON} {config.UI_TITLE}")
    st.subheader(config.UI_SUBTITLE)
    
    # Set custom styles
    st.markdown("""
    <style>
    .user-message {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .assistant-message {
        background-color: #e6f3ff;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .approval-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .tool-header {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .tool-args {
        font-family: monospace;
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    setup_page()
    
    # Initialize session state
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.messages = []
        st.session_state.passenger_id = config.DEFAULT_PASSENGER_ID
        st.session_state.pending_approval = False
    
    # Setup sidebar
    setup_sidebar()
    
    # Main chat interface
    chat_interface = ChatInterface()
    chat_interface.render()


if __name__ == "__main__":
    main()