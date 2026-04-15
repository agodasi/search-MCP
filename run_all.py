import subprocess
import time
import signal
import sys
import os

def run_all():
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

    print("🚀 Starting Search-MCP System...")

    try:
        # 1. Start the Bridge
        print("Step 1: Starting Communication Bridge (bridge.py)...")
        p_bridge = subprocess.Popen(["uv", "run", "python", "bridge.py"])
        processes.append(p_bridge)
        time.sleep(3)  # Wait for bridge to be ready

        # 2. Start the MCP Server
        print("Step 2: Starting MCP Server (mcp_server.py)...")
        p_mcp = subprocess.Popen(["uv", "run", "python", "mcp_server.py"])
        processes.append(p_mcp)
        time.sleep(3)  # Wait for MCP server to be ready

        # 3. Start the GUI
        print("Step 3: Starting Monitoring GUI (gui_app.py)...")
        p_gui = subprocess.Popen(["uv", "run", "python", "gui_app.py"])
        processes.append(p_gui)

        print("\n✅ All components are running!")
        print("Press Ctrl+C to stop all processes.")

        # Keep the main process alive
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        for p in processes:
            p.terminate()
        sys.exit(1)

if __name__ == "__main__":
    run_all()