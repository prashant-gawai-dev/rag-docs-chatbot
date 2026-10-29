#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend" / "source"
FRONTEND_DIR = ROOT / "frontend"
VENV_DIR = ROOT / ".venv"


def find_python_in_venv():
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_python_env():
    python_exe = find_python_in_venv()
    if not python_exe.exists():
        print("Creating virtual environment in .venv...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)

    if not python_exe.exists():
        raise FileNotFoundError(f"Unable to create virtual environment at {VENV_DIR}")

    return str(python_exe)


def install_backend_requirements(python_exe: str):
    requirements_file = BACKEND_DIR / "requirements.txt"
    if not requirements_file.exists():
        print(f"No backend requirements file found at {requirements_file}")
        return

    print("Checking backend Python dependencies...")
    subprocess.run(
        [python_exe, "-m", "pip", "install", "-r", str(requirements_file)],
        check=False,
    )


def ensure_frontend_dependencies():
    if not shutil.which("npm"):
        raise RuntimeError("Node.js / npm is not installed or not on PATH. Please install Node.js to run the frontend.")

    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)


def start_backend(python_exe: str):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)

    cmd = [
        python_exe,
        "-m",
        "uvicorn",
        "api.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload",
    ]
    print(f"Starting backend: {' '.join(cmd)}")
    return subprocess.Popen(cmd, cwd=str(BACKEND_DIR), env=env)


def start_frontend():
    cmd = ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
    print(f"Starting frontend: {' '.join(cmd)}")
    return subprocess.Popen(cmd, cwd=str(FRONTEND_DIR), env=os.environ.copy())


def stop_process(process):
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def main():
    print("Starting the RAG Docs Chatbot...")

    backend_python = ensure_python_env()
    install_backend_requirements(backend_python)
    ensure_frontend_dependencies()

    backend_proc = start_backend(backend_python)
    frontend_proc = start_frontend()

    print("\nServices are starting:")
    print("- Backend: http://127.0.0.1:8000")
    print("- Frontend: http://127.0.0.1:5173")
    print("\nPress Ctrl+C to stop both services.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        stop_process(backend_proc)
        stop_process(frontend_proc)
        print("All services stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
