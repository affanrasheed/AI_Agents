"""
Entry point for the Travel Assistant application.
"""
import os
import sys
import streamlit as st
from pathlib import Path

# Add the project root to PYTHONPATH
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Print debug information
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

# If running with streamlit, add a launcher message
if any(arg.endswith("streamlit") for arg in sys.argv):
    print("Starting Swiss Airlines Travel Assistant...", file=sys.stderr)

# This is only for directly running the main.py file
# Streamlit looks for the main function in the UI app

if __name__ == "__main__":
    # If not run with streamlit, launch streamlit
    if not any(arg.endswith("streamlit") for arg in sys.argv):
        import subprocess
        subprocess.run([
            "streamlit", "run", 
            os.path.join(project_root, "ui", "app.py")
        ])
    else:
        # If run with streamlit, the app.main will be called by streamlit
        pass