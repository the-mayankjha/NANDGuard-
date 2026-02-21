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
    
    # Detect if running as a bundled executable (PyInstaller)
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # In a frozen app, skip venv check and run dashboard directly
        print("Running in frozen mode...")
        # Add internal path to sys.path for PyInstaller layout
        if hasattr(sys, '_MEIPASS'):
            if sys._MEIPASS not in sys.path:
                sys.path.insert(0, sys._MEIPASS)
        
        from dashboard.qt_app import run_app
        run_app()
        return

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
    
    # Run dashboard (Development mode)
    dashboard_path = os.path.join(base_dir, "dashboard", "qt_app.py")
    args = [sys.executable, dashboard_path]
    if not has_tkinter:
        args.append("--cli")
    
    # Ensure project root is in PYTHONPATH so sub-scripts find packages
    env = os.environ.copy()
    env["PYTHONPATH"] = base_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    subprocess.run(args, env=env)

if __name__ == "__main__":
    main()
