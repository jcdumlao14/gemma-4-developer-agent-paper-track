import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
cmd = [sys.executable, "-m", "trace_research.cli", "run-demo"]
completed = subprocess.run(cmd, cwd=root, check=False)
raise SystemExit(completed.returncode)
