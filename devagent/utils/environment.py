import os
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict

@dataclass
class EnvironmentInfo:
    type: str = "unknown"  # pip, poetry, conda, etc.
    python_version: str = "unknown"
    dependencies: List[str] = field(default_factory=list)
    markers: List[str] = field(default_factory=list)
    install_success: bool = False
    last_fingerprint: Optional[float] = None
    failures: List[str] = field(default_factory=list)

class EnvironmentDetector:
    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
        self.markers = {
            "requirements.txt": "pip",
            "pyproject.toml": "modern/poetry/flit",
            "poetry.lock": "poetry",
            "Pipfile": "pipenv",
            "environment.yml": "conda",
            "setup.py": "setuptools"
        }

    def detect(self) -> EnvironmentInfo:
        info = EnvironmentInfo()
        found_markers = []

        for marker, env_type in self.markers.items():
            marker_path = os.path.join(self.project_path, marker)
            if os.path.exists(marker_path):
                found_markers.append(marker)
                # Primary type detection (prioritize modern tools)
                if info.type == "unknown" or env_type in ["poetry", "modern/poetry/flit"]:
                    info.type = env_type
        
        info.markers = found_markers
        
        # Try to parse dependencies from common files
        if "requirements.txt" in found_markers:
            info.dependencies.extend(self._parse_requirements())
        
        return info

    def _parse_requirements(self) -> List[str]:
        req_path = os.path.join(self.project_path, "requirements.txt")
        deps = []
        try:
            with open(req_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        deps.append(line)
        except Exception:
            pass
        return deps

    def setup_isolated_env(self, env_name: str = "validation_env") -> str:
        """Creates a venv and installs dependencies."""
        env_path = os.path.join(self.project_path, ".tmp_envs", env_name)
        python_exe = os.path.join(env_path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(env_path, "bin", "python")
        
        if os.path.exists(python_exe):
            print(f"[ENV] Found existing virtual environment at {env_path}")
            return python_exe

        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        
        import venv
        import subprocess
        
        print(f"[ENV] Creating virtual environment at {env_path}...")
        venv.create(env_path, with_pip=True)
        
        info = self.detect()
        
        # Install dependencies
        if info.type == "pip":
            req_path = os.path.join(self.project_path, "requirements.txt")
            print(f"[ENV] Installing dependencies from {req_path}...")
            try:
                subprocess.check_call([python_exe, "-m", "pip", "install", "-r", req_path])
                info.install_success = True
            except subprocess.CalledProcessError as e:
                info.failures.append(f"Install failed: {str(e)}")
                info.install_success = False
        
        # Validate installation
        try:
            subprocess.check_call([python_exe, "-m", "pip", "check"])
            print("[ENV] Runtime health check passed.")
        except subprocess.CalledProcessError:
            print("[ENV] Runtime health check found conflicts.")
            info.failures.append("Dependency conflicts detected.")
            
        self.save_fingerprint(info)
        return python_exe

    def repair_dependencies(self, missing_package: str, env_name: str = "validation_env") -> bool:
        """Attempts to install a missing package into the venv."""
        env_path = os.path.join(self.project_path, ".tmp_envs", env_name)
        python_exe = os.path.join(env_path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(env_path, "bin", "python")
        
        if not os.path.exists(python_exe):
            return False
            
        import subprocess
        print(f"[ENV] Repairing environment: Installing missing package '{missing_package}'...")
        try:
            subprocess.check_call([python_exe, "-m", "pip", "install", missing_package])
            return True
        except subprocess.CalledProcessError:
            return False

    def save_fingerprint(self, info: EnvironmentInfo):
        fingerprint_path = os.path.join(self.project_path, ".devagent_env.json")
        with open(fingerprint_path, 'w') as f:
            json.dump(asdict(info), f, indent=2)

    @staticmethod
    def load_fingerprint(project_path: str) -> Optional[Dict]:
        fingerprint_path = os.path.join(project_path, ".devagent_env.json")
        if os.path.exists(fingerprint_path):
            with open(fingerprint_path, 'r') as f:
                return json.load(f)
        return None
