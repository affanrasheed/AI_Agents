"""
Simple script to run the Travel Assistant application.
This is a more direct approach to launching the Streamlit app.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the Travel Assistant application."""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Print debug information
    print(f"Project root: {project_root}")
    
    # Get the full path to ui/app.py
    app_path = os.path.join(project_root, "ui", "app.py")
    print(f"Launching Streamlit with app at: {app_path}")
    
    # Run Streamlit with the UI app
    try:
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.headless", "true",
            "--browser.serverAddress", "localhost",
            "--server.port", "8501"
        ], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        return e.returncode
    except FileNotFoundError:
        print("Error: Streamlit module not found. Make sure Streamlit is installed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())