import os
import sys
import subprocess

def main():
    # The directory where THIS script is located
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main.py entry point
    main_py = os.path.join(agent_dir, "main.py")
    
    # Path to the python executable in the conda environment
    # On Windows, it's typically in the environment's bin or root folder.
    # We'll use the current sys.executable which should be the conda one.
    python_exe = sys.executable
    
    # Run the command, forwarding all arguments
    cmd = [python_exe, main_py] + sys.argv[1:]
    
    # Execute
    try:
        # Set PYTHONPATH so 'app', 'tools', etc. can be found
        env = os.environ.copy()
        env["PYTHONPATH"] = agent_dir + os.pathsep + env.get("PYTHONPATH", "")
        
        result = subprocess.run(cmd, env=env)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running DevAgent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
