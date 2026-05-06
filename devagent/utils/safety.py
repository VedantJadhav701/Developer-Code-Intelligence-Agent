"""
Safety Manager — handles snapshots and rollbacks.
"""

import os
import shutil
import time
from rich.console import Console
from devagent.tools.git_tools import is_git_repo

console = Console()

class SafetyManager:
    def __init__(self, project_root: str):
        self.root = os.path.abspath(project_root)
        self.snapshot_dir = os.path.join(self.root, ".devagent_backups")
        
    def create_snapshot(self, task_id: str = "latest") -> str:
        """Create a safety snapshot of the current project state."""
        if is_git_repo(self.root):
            # For git repos, we rely on the user's ability to git checkout
            # but we could also do a 'git stash' here for safety.
            return "git"

        # For non-git repos, we do a physical backup of .py files
        os.makedirs(self.snapshot_dir, exist_ok=True)
        timestamp = int(time.time())
        dest = os.path.join(self.snapshot_dir, f"{task_id}_{timestamp}")
        
        # Simple copy of python files
        os.makedirs(dest, exist_ok=True)
        for root, _, files in os.walk(self.root):
            if ".devagent" in root or "venv" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    src_file = os.path.join(root, f)
                    rel_path = os.path.relpath(src_file, self.root)
                    target_file = os.path.join(dest, rel_path)
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    shutil.copy2(src_file, target_file)
        
        # Save metadata
        metadata = {
            "task_id": task_id,
            "timestamp": timestamp,
            "root": self.root
        }
        with open(os.path.join(dest, "metadata.json"), "w") as f:
            import json
            json.dump(metadata, f, indent=2)

        return dest

    def rollback(self, snapshot_id: str = "latest") -> bool:
        """Rollback the project to a previous snapshot."""
        if is_git_repo(self.root):
            console.print("[bold yellow][SAFETY][/bold yellow] This is a Git repository. Use [bold cyan]git checkout .[/bold cyan] to rollback.")
            return False

        # Find latest snapshot if not specified
        if not os.path.exists(self.snapshot_dir):
            console.print("[bold red][ERROR][/bold red] No snapshots found.")
            return False
            
        snapshots = sorted(os.listdir(self.snapshot_dir))
        if not snapshots:
            console.print("[bold red][ERROR][/bold red] No snapshots found.")
            return False
            
        target = os.path.join(self.snapshot_dir, snapshots[-1])
        console.print(f"[bold yellow][SAFETY][/bold yellow] Rolling back from {target}...")
        
        # Restore files
        for root, _, files in os.walk(target):
            for f in files:
                src_file = os.path.join(root, f)
                rel_path = os.path.relpath(src_file, target)
                dest_file = os.path.join(self.root, rel_path)
                shutil.copy2(src_file, dest_file)
        
        console.print("[bold green]Rollback complete.[/bold green]")
        return True
