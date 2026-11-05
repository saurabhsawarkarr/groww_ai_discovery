import os
import sys
import subprocess
from pathlib import Path

# Set project root
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

app_path = str(PROJECT_ROOT / "src" / "ui" / "app.py")
print(f"Launching Groww Discovery Engine on http://127.0.0.1:8501...", flush=True)

cmd = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    app_path,
    "--server.port=8501",
    "--server.headless=true",
    "--server.address=127.0.0.1",
    "--browser.gatherUsageStats=false",
    "--server.enableCORS=false",
    "--server.enableXsrfProtection=false",
]

subprocess.run(cmd)
