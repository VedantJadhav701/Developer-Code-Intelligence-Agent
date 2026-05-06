import os
from devagent.utils.environment import EnvironmentDetector

def get_environment_info(project_path: str):
    """
    Detects the project environment (pip, poetry, etc.) and lists dependencies.
    Useful for understanding what the project needs to run.
    """
    project_path = os.path.abspath(project_path)
    detector = EnvironmentDetector(project_path)
    info = detector.detect()
    
    # Auto-setup venv if it's the first run or fingerprint missing install_success
    fingerprint = detector.load_fingerprint(project_path)
    if not fingerprint or not fingerprint.get("install_success"):
        detector.setup_isolated_env()
        info = detector.detect() # Refresh info
    
    # Save fingerprint for observability
    detector.save_fingerprint(info)
    
    return {
        "status": "success",
        "environment": {
            "type": info.type,
            "markers_found": info.markers,
            "dependency_count": len(info.dependencies),
            "dependencies": info.dependencies[:20] # Limit output
        }
    }

def repair_environment(package_name: str, project_path: str):
    """
    Attempts to install a missing package into the project environment.
    Use this if you see ModuleNotFoundError or missing dependency errors.
    """
    project_path = os.path.abspath(project_path)
    detector = EnvironmentDetector(project_path)
    success = detector.repair_dependencies(package_name)
    
    if success:
        return {"status": "success", "message": f"Successfully installed {package_name}"}
    else:
        return {"status": "error", "message": f"Failed to install {package_name}"}
