import subprocess
import time
import signal
import sys
import os
import webbrowser

def get_python_executable():
    """Returns the path to the project's .venv python executable if it exists, otherwise sys.executable."""
    # Windows
    venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    # Linux/Mac fallback
    venv_python_posix = os.path.join(os.getcwd(), ".venv", "bin", "python")
    if os.path.exists(venv_python_posix):
        return venv_python_posix
    return sys.executable

def run_all():
    python_exe = get_python_executable()
    print(f"Using Python: {python_exe}")
    processes = []

    def signal_handler(sig, frame):
        print("\nStopping all components...")
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        sys.exit(0)

    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting Search-MCP System...")

    try:
        # 1. Start the Bridge
        print("Step 1: Starting Communication Bridge (bridge.py)...")
        p_bridge = subprocess.Popen([python_exe, "bridge.py"])
        processes.append(p_bridge)
        time.sleep(3)  # Wait for bridge to be ready

        # 2. Start the MCP Server
        print("Step 2: Starting MCP Server (mcp_server.py)...")
        p_mcp = subprocess.Popen([python_exe, "mcp_server.py"])
        processes.append(p_mcp)
        time.sleep(3)  # Wait for MCP server to be ready

        # 3. Start the GUI
        print("Step 3: Starting Monitoring GUI (gui_app.py)...")
        p_gui = subprocess.Popen([python_exe, "gui_app.py"])
        processes.append(p_gui)
        time.sleep(5)  # Wait for GUI to be ready

        print("\nAll components are running! The GUI should now be open as a native app.")
        print("\nAll components are running!")
        print("Press Ctrl+C to stop all processes.")

        # Keep the main process alive until GUI is closed
        while True:
            if p_gui.poll() is not None:
                print("\nGUI process terminated. Stopping system...")
                break
            time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        sys.exit(0)

if __name__ == "__main__":
    run_all()