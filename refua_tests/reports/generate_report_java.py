"""
Generate Allure Report using Java directly
Bypasses npm wrapper bug with spaces in Windows username
"""
import subprocess
import os
import webbrowser
from pathlib import Path

def _candidate_allure_lib_dirs() -> list[Path]:
    """Resolve allure-commandline lib dirs across common Windows install locations."""
    candidates: list[Path] = []

    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(
            Path(appdata) / "npm" / "node_modules" / "allure-commandline" / "dist" / "lib"
        )

    # Global npm root (often Program Files\\nodejs\\node_modules on Windows)
    try:
        npm_root = subprocess.run(
            ["npm", "root", "-g"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if npm_root:
            candidates.append(
                Path(npm_root) / "allure-commandline" / "dist" / "lib"
            )
    except (OSError, subprocess.CalledProcessError):
        pass

    # Scoop install
    scoop_allure = Path.home() / "scoop" / "apps" / "allure" / "current"
    if scoop_allure.exists():
        for lib in scoop_allure.rglob("allure-commandline*.jar"):
            candidates.append(lib.parent)

    # De-dupe while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in candidates:
        resolved = path.resolve() if path.exists() else path
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def generate_report_with_java():
    """Generate Allure report using Java"""

    # Get project root (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent

    allure_lib = None
    allure_jar = []
    searched = []
    for candidate in _candidate_allure_lib_dirs():
        searched.append(str(candidate))
        jars = list(candidate.glob("allure-commandline*.jar")) if candidate.exists() else []
        if jars:
            allure_lib = candidate
            allure_jar = jars
            break

    if not allure_jar or allure_lib is None:
        print("[ERROR] Allure JAR not found")
        print("Searched:")
        for path in searched:
            print(f"  - {path}")
        print("Install: npm install -g allure-commandline")
        return False

    allure_jar = allure_jar[0]
    print(f"[OK] Found Allure JAR: {allure_jar.name}")
    print(f"[OK] Lib dir: {allure_lib}")

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

    except FileNotFoundError:
        print("[ERROR] Java not found on PATH.")
        print('Set JAVA_HOME first, e.g.:')
        print('  $env:JAVA_HOME="C:\\Program Files\\Eclipse Adoptium\\jdk-17.0.20.8-hotspot"')
        print('  $env:Path = "$env:JAVA_HOME\\bin;$env:Path"')
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
