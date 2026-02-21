import os
import platform
import plistlib

def setup_autostart(enable=True):
    """Sets up auto-start for macOS using LaunchAgents."""
    if platform.system() != "Darwin":
        return False, "Auto-start is currently only implemented for macOS."
    
    label = "com.nandguard.plus"
    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
    
    if not enable:
        if os.path.exists(plist_path):
            os.remove(plist_path)
        return True, "Auto-start disabled."
    
    # Get project root and python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_path = os.path.join(project_root, "venv", "bin", "python")
    main_script = os.path.join(project_root, "main.py")
    
    if not os.path.exists(python_path):
        python_path = "python3" # Fallback
        
    plist_data = {
        "Label": label,
        "ProgramArguments": [python_path, main_script],
        "RunAtLoad": True,
        "ProcessType": "Interactive",
        "WorkingDirectory": project_root
    }
    
    try:
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)
        with open(plist_path, 'wb') as f:
            plistlib.dump(plist_data, f)
        return True, "Auto-start enabled."
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, msg = setup_autostart()
    print(f"Result: {success}, Message: {msg}")
