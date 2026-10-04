"""
Generate Allure HTML Report
Workaround for spaces in Windows username path
"""
import subprocess
import os
import shutil
import webbrowser
from pathlib import Path

def generate_allure_report():
    """Generate Allure HTML report and open in browser"""

    # Get project root (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent

    # Paths relative to project root
    allure_results = project_root / "allure" / "results"
    allure_report = project_root / "allure" / "report"

    # Get AppData from environment
    appdata = os.environ.get("APPDATA")
    if not appdata:
        print("[ERROR] APPDATA environment variable not found")
        return False

    print(f"[OK] AppData: {appdata}")

    # Allure binary path
    allure_bin = Path(appdata) / "npm" / "node_modules" / "allure-commandline" / "bin" / "allure"

    if not allure_bin.is_file():
        print(f"[ERROR] Allure not found at: {allure_bin}")
        print("Install with: npm install -g allure-commandline")
        return False

    node_bin = shutil.which("node")
    if not node_bin:
        print("[ERROR] Node.js not found on PATH")
        return False

    print(f"[OK] Found allure: {allure_bin}")

    # Generate report
    print("\n[INFO] Generating Allure HTML report...")
    try:
        cmd = [
            node_bin,
            str(allure_bin.resolve()),
            "generate",
            str(allure_results.resolve()),
            "-o",
            str(allure_report.resolve()),
            "--clean"
        ]

        result = subprocess.run(
            cmd,
            shell=False,
            check=True,
            capture_output=True,
            text=True
        )

        print("[OK] Report generated successfully!")

        # Open report in browser
        index_html = allure_report / "index.html"
        if index_html.exists():
            print(f"\n[OK] Opening report: {index_html}")
            webbrowser.open(str(index_html.absolute()))
            print("\n" + "="*60)
            print(f"Report location: {allure_report.absolute()}")
            print(f"Open manually: {index_html.absolute()}")
            print("="*60)
            return True
        else:
            print(f"[ERROR] Report index.html not found: {index_html}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error generating report:")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Allure Report Generator")
    print("="*60 + "\n")

    success = generate_allure_report()

    if not success:
        print("\n" + "="*60)
        print("Alternative: Run manually in CMD:")
        print('  allure generate allure/results -o allure/report --clean')
        print('  start allure\\report\\index.html')
        print("="*60)
