import argparse
import sys
import os
import subprocess
import time
import signal

def get_launch_command(mode):
    """Get the correct command to launch a child process in both python and PyInstaller frozen modes."""
    if getattr(sys, 'frozen', False):
        # When frozen, sys.executable is the .exe itself. 
        # We use the same .exe with a different mode flag.
        return [sys.executable, "--mode", mode]
    else:
        return [sys.executable, sys.argv[0], "--mode", mode]

def suppress_output():
    """Redirect stdout and stderr to devnull to prevent any console interaction."""
    if getattr(sys, 'frozen', False):
        f = open(os.devnull, 'w')
        sys.stdout = f
        sys.stderr = f

def run_all_mode():
    print("Starting Search-MCP System (All-in-one Mode)...")
    processes = []

    def signal_handler(sig, frame):
        print("\nStopping all components...")
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # On Windows, use CREATE_NO_WINDOW to prevent child console windows
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        print("Step 1: Starting Communication Bridge...")
        p_bridge = subprocess.Popen(
            get_launch_command("bridge"), 
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(p_bridge)
        time.sleep(3)

        print("Step 2: Starting MCP Server...")
        p_mcp = subprocess.Popen(
            get_launch_command("mcp"), 
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(p_mcp)
        time.sleep(3)

        print("Step 3: Starting Monitoring GUI...")
        p_gui = subprocess.Popen(
            get_launch_command("gui"), 
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(p_gui)
        time.sleep(2)

        print("\nAll components are running!")
        print("Press Ctrl+C to stop all processes.")

        # Keep alive until GUI closes
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

def main():
    parser = argparse.ArgumentParser(description="Search-MCP Entry Point")
    parser.add_argument("--mode", choices=["all", "mcp", "bridge", "gui"], default="all", help="Component to run")
    
    # GUI modes specific arguments (like Flet's internal arguments) might cause issues if parse_args is strict.
    # We use parse_known_args in case Flet appends arguments behind the scenes.
    args, _ = parser.parse_known_args()
    
    # Suppress console output for frozen executables
    suppress_output()

    if args.mode == "mcp":
        import mcp_server
        import threading
        import asyncio
        
        def start_listener():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(mcp_server.listen_to_bridge())

        listener_thread = threading.Thread(target=start_listener, daemon=True)
        listener_thread.start()
        
        mcp_server.mcp.run()
        sys.exit(0)
        
    elif args.mode == "bridge":
        import bridge
        import uvicorn
        from config_manager import load_config
        config = load_config()
        port = config.get("port", 8002)
        uvicorn.run(bridge.app, host="0.0.0.0", port=port)
        sys.exit(0)
        
    elif args.mode == "gui":
        import gui_app
        import flet as ft
        # Since we changed app startup recently in gui_app
        # Make sure gui_app.py uses main directly
        # Check if FLET_WEB_PORT or --web exists
        # Use the assets directory relative to the script/exe
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")
        
        if os.getenv("FLET_WEB_PORT") or "--web" in sys.argv:
            port = int(os.getenv("FLET_WEB_PORT", 8550))
            ft.app(target=gui_app.main, view=ft.AppView.WEB_BROWSER, port=port, assets_dir=assets_dir)
        else:
            ft.app(target=gui_app.main, assets_dir=assets_dir)
        sys.exit(0)
        
    elif args.mode == "all":
        run_all_mode()

if __name__ == "__main__":
    if sys.platform == "win32":
        # Required for proper multiprocessing support in frozen windows executables 
        # (Though we are using subprocess, so it's less strictly needed, but good practice if submodules use multiprocessing)
        import multiprocessing
        multiprocessing.freeze_support()
        
    main()
