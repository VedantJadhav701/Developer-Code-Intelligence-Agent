import sys
import os
import json
from dataclasses import asdict

# Add project root to path
sys.path.append(r"c:\Users\HP\projects\Developer-Code-Intelligence-Agent")

from devagent.tools.env_detector import get_environment_info
from devagent.utils.environment import EnvironmentDetector

project_path = r"c:\Users\HP\projects\Developer-Code-Intelligence-Agent\demo_project"
detector = EnvironmentDetector(project_path)

# Test Phase 1: Detection
info = detector.detect()
print("Environment Detection Result:")
print(json.dumps(asdict(info), indent=2))

# Test Phase 2: Isolated Setup
print("\n--- Testing Phase 2: Isolated Setup ---")
python_exe = detector.setup_isolated_env("test_env")
print(f"Isolated Python EXE: {python_exe}")

# Verify python version in the venv
import subprocess
version = subprocess.check_output([python_exe, "--version"], text=True).strip()
print(f"Isolated Python Version: {version}")

# Check installed packages
packages = subprocess.check_output([python_exe, "-m", "pip", "list"], text=True)
print("\nInstalled Packages in Isolated Env:")
print(packages)

# Check for fingerprint file
fingerprint_path = os.path.join(project_path, ".devagent_env.json")
if os.path.exists(fingerprint_path):
    print(f"\nFingerprint saved successfully to: {fingerprint_path}")
    with open(fingerprint_path, 'r') as f:
        print(json.dumps(json.load(f), indent=2))
else:
    print("\nFingerprint NOT found!")
