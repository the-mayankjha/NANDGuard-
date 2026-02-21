import os
import subprocess
import sys
import platform

def main():
    print("NANDGuard – Smart Storage Health Monitor")
    print("-----------------------------------------------")
    
    # Get the directory where main.py is located
    project_root = os.path.dirname(os.path.abspath(__file__))
    base_dir = project_root
    
    # Check for tkinter availability
    try:
        import tkinter
        has_tkinter = True
    except ImportError:
        has_tkinter = False
        print("\n[!] GUI ERROR: Tkinter not found.")
        if platform.system() == "Darwin":
            print("On macOS with Homebrew, you need to install it manually:")
            print(">>> brew install python-tk@3.13")
        elif platform.system() == "Linux":
            print("On Linux, use your package manager (e.g., sudo apt install python3-tk)")
        print("\nLaunching CLI mode as a fallback...")

    # Check if we are in venv, if not, try to use it
    is_windows = platform.system() == "Windows"
    venv_bin = "Scripts" if is_windows else "bin"
    python_exe = "python.exe" if is_windows else "python"
    
    venv_python = os.path.join(project_root, "venv", venv_bin, python_exe)
    
    if os.path.exists(venv_python) and sys.executable != venv_python:
        print("Restarting with virtual environment...")
        if is_windows:
            subprocess.run([venv_python] + sys.argv)
            sys.exit()
        else:
            os.execv(venv_python, [venv_python] + sys.argv)
    
    # Run dashboard
    dashboard_path = os.path.join(base_dir, "dashboard", "app.py")
    args = [sys.executable, dashboard_path]
    if not has_tkinter:
        args.append("--cli")
    
    subprocess.run(args)

if __name__ == "__main__":
    main()
