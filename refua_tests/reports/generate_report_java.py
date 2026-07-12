"""
Generate Allure Report using Java directly
Bypasses npm wrapper bug with spaces in Windows username
"""
import subprocess
import os
import webbrowser
from pathlib import Path

def generate_report_with_java():
    """Generate Allure report using Java"""

    # Get project root (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent

    # Paths
    appdata = os.environ.get("APPDATA")
    allure_dir = Path(appdata) / "npm" / "node_modules" / "allure-commandline"
    allure_lib = allure_dir / "dist" / "lib"
    allure_jar = list(allure_lib.glob("allure-commandline*.jar"))

    if not allure_jar:
        print("[ERROR] Allure JAR not found")
        print(f"Expected location: {allure_lib}")
        return False

    allure_jar = allure_jar[0]
    print(f"[OK] Found Allure JAR: {allure_jar.name}")

    # Build classpath (all JARs in lib directory)
    jars = list(allure_lib.glob("*.jar"))
    classpath = ";".join(str(jar) for jar in jars)

    # Paths for report generation (relative to project root)
    results_dir = (project_root / "allure" / "results").absolute()
    report_dir = (project_root / "allure" / "report").absolute()

    if not results_dir.exists():
        print(f"[ERROR] Results directory not found: {results_dir}")
        return False

    print(f"[OK] Results: {results_dir}")
    print(f"[OK] Output: {report_dir}")
    print()
    print("[INFO] Generating report with Java...")

    try:
        # Call Java directly
        cmd = [
            "java",
            "-cp", classpath,
            "io.qameta.allure.CommandLine",
            "generate",
            str(results_dir),
            "-o", str(report_dir),
            "--clean"
        ]

        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        print("[OK] Report generated successfully!")
        print()

        # Open report
        index_html = report_dir / "index.html"
        if index_html.exists():
            print("=" * 60)
            print(f"Report: {index_html}")
            print("=" * 60)
            print()
            print("[OK] Opening report in browser...")
            webbrowser.open(str(index_html))
            return True
        else:
            print(f"[ERROR] index.html not found: {index_html}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to generate report:")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Allure Report Generator (Java Direct)")
    print("=" * 60)
    print()
    generate_report_with_java()
