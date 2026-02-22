import os
import subprocess
import sys
import platform
import ctypes

def is_admin():
    """Check if the current process has administrative privileges."""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.getuid() == 0
    except AttributeError:
        return False

def request_elevation():
    """Relaunches the application with administrative privileges if necessary."""
    if is_admin():
        return True

    print("\n[!] ELEVATION REQUIRED: This utility needs root privileges for hardware access.")
    
    # Get current script path and arguments
    is_frozen = getattr(sys, 'frozen', False)
    script_path = os.path.abspath(sys.argv[0])
    args = sys.argv[1:]
    
    if platform.system() == "Darwin":
        # macOS: Use osascript for a graphical password prompt
        # For frozen apps, sys.executable is the binary itself
        if is_frozen:
            inner_cmd = f'\\"{sys.executable}\\" {" ".join(args)}'
        else:
            inner_cmd = f'{sys.executable} \\"{script_path}\\" {" ".join(args)}'
            
        cmd = f'do shell script "{inner_cmd}" with administrator privileges'
        try:
            subprocess.run(['osascript', '-e', cmd], check=True)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print("Elevation cancelled by user.")
            return False
            
    elif platform.system() == "Linux":
        # Linux: Try pkexec (graphical) or sudo (terminal)
        exec_args = [sys.executable]
        if not is_frozen:
            exec_args.append(script_path)
        exec_args.extend(args)
        
        if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
            try:
                subprocess.run(['pkexec'] + exec_args, check=True)
                sys.exit(0)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # Fallback to sudo in terminal
        try:
            subprocess.run(['sudo'] + exec_args, check=True)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print("Elevation failed.")
            return False
            
    return True

def setup_environment():
    """Expand PATH to ensure system tools like smartctl are discoverable."""
    common_paths = [
        "/usr/local/bin",
        "/opt/homebrew/bin",
        "/usr/sbin",
        "/sbin",
        "/bin",
        "/usr/bin"
    ]
    current_path = os.environ.get("PATH", "")
    for p in common_paths:
        if p not in current_path:
            current_path = f"{p}{os.pathsep}{current_path}"
    os.environ["PATH"] = current_path
    
    # Also update for the current process
    if platform.system() != "Windows":
        sys.path.append("/usr/local/lib/python3.13/site-packages")

def main():
    print("NANDGuard – Smart Storage Health Monitor")
    print("-----------------------------------------------")
    
    # Expand PATH for hardware tool discovery
    setup_environment()
    
    # Request elevation for hardware access
    if not request_elevation():
        print("Hardware access will be limited to non-root telemetry.")

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
    
    # Also pass the updated PATH to the subprocess
    env["PATH"] = os.environ["PATH"]
    
    subprocess.run(args, env=env)

if __name__ == "__main__":
    main()
