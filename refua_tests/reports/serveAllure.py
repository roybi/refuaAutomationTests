"""
Allure Report Server
Direct invocation bypassing npm wrapper bug
"""
import subprocess
import os
import shutil
import time
import webbrowser
from pathlib import Path

def serve_allure_report():
    """Start Allure server and open browser"""

    # Get project root (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent

    # Get paths
    appdata = os.environ.get("APPDATA")
    allure_bin = Path(appdata) / "npm" / "node_modules" / "allure-commandline" / "bin" / "allure"
    allure_results = project_root / "allure" / "results"

    if not allure_bin.is_file():
        print("[ERROR] Allure not found. Install with: npm install -g allure-commandline")
        return False

    node_bin = shutil.which("node")
    if not node_bin:
        print("[ERROR] Node.js not found on PATH")
        return False

    if not allure_results.exists():
        print("[ERROR] allure/results folder not found")
        return False

    print("=" * 60)
    print("Starting Allure Report Server")
    print("=" * 60)
    print(f"Results: {allure_results.absolute()}")
    print(f"Allure: {allure_bin}")
    print()
    print("[INFO] Generating report and starting server...")
    print("[INFO] Server will start on http://localhost (random port)")
    print("[INFO] Browser will open automatically")
    print("[INFO] Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    try:
        # Call node directly with properly quoted paths
        cmd = [
            node_bin,
            str(allure_bin.resolve()),
            "serve",
            str(allure_results.resolve())
        ]

        # Start the process
        process = subprocess.Popen(
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Monitor output and look for URL
        url_opened = False
        for line in process.stdout:
            print(line, end='')

            # Look for server URL and open browser
            if not url_opened and "Server started at" in line:
                # Extract URL from line
                if "http://" in line:
                    try:
                        url = line.split("http://")[1].split()[0]
                        url = f"http://{url}"
                        print(f"\n[OK] Opening browser: {url}\n")
                        time.sleep(2)  # Wait for server to fully start
                        webbrowser.open(url)
                        url_opened = True
                    except Exception as e:
                        print(f"[WARN] Could not auto-open browser: {e}")

        process.wait()

    except KeyboardInterrupt:
        print("\n\n[INFO] Shutting down server...")
        process.terminate()
        process.wait()
        print("[OK] Server stopped")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    return True

if __name__ == "__main__":
    serve_allure_report()
