#!/usr/bin/env python
"""Start the conflict tracker scraper and API in one command."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "tutorial_Selenium"


def run_scraper() -> None:
    print("Starting scraper...")
    result = subprocess.run([sys.executable, "sql.py"], cwd=APP_DIR)
    if result.returncode == 0:
        print("Scraper finished.")
    else:
        print(f"Scraper exited with code {result.returncode}; starting the API anyway.")


def run_server() -> None:
    print("Starting API server on http://localhost:8000 ...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        cwd=APP_DIR,
        check=False,
    )


if __name__ == "__main__":
    run_scraper()
    run_server()
