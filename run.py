"""Entry point to run the Streamlit web app."""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/app.py", *sys.argv[1:]])
