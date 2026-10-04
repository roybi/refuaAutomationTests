"""
Serve Allure Report via HTTP Server
Fixes CORS and file:// protocol issues that cause missing images/icons
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_report(port=8000):
    """Start HTTP server for Allure report"""

    # Get project root (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    report_dir = project_root / "allure" / "report"

    if not report_dir.exists():
        print("[ERROR] allure/report folder not found")
        print("Run: python -m refua_tests.reports.generateReportJava first")
        return False

    # Save current directory
    original_dir = os.getcwd()

    # Change to report directory
    os.chdir(report_dir)

    print("=" * 60)
    print("Allure Report Server")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"URL: http://localhost:{port}")
    print()
    print("[INFO] Starting server...")
    print("[INFO] Press Ctrl+C to stop")
    print("=" * 60)
    print()

    try:
        # Create server
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}"
            print(f"[OK] Server started: {url}")
            print(f"[OK] Opening browser...")
            print()

            # Open browser
            webbrowser.open(url)

            # Serve forever
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n[INFO] Shutting down server...")
        print("[OK] Server stopped")
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"[ERROR] Port {port} is already in use")
            print(f"Try: python -m refua_tests.reports.serveHttp --port {port + 1}")
        else:
            print(f"[ERROR] {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    finally:
        # Restore original directory
        os.chdir(original_dir)

    return True

if __name__ == "__main__":
    import sys

    port = 8000
    if len(sys.argv) > 1 and sys.argv[1] == "--port":
        port = int(sys.argv[2])

    serve_report(port)
