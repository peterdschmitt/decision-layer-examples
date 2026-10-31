"""Run every example's offline routing checks. No key or network needed."""

import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
failed = 0
for name in sorted(os.listdir(ROOT)):
    folder = os.path.join(ROOT, name)
    if os.path.isfile(os.path.join(folder, "test_route.py")):
        print(f"== {name}")
        failed |= subprocess.call([sys.executable, "-m", "unittest", "-q", "test_route"], cwd=folder)
sys.exit(failed)
