import os
import pathlib
import signal
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVICE_PORTS = {"identity": 50051, "video": 50052, "messaging": 50053}
GATEWAY_COMMAND = [
    sys.executable,
    "-m",
    "gunicorn",
    "--bind",
    "127.0.0.1:8000",
    "--workers",
    "1",
    "--threads",
    "8",
    "vgm.gateway:app",
]


def environment():
    if not os.getenv("DATABASE_URL"):
        raise SystemExit(
            "Set DATABASE_URL to your local PostgreSQL database first."
        )

    result = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "backend"),
        "PUBLIC_ORIGIN": os.getenv("PUBLIC_ORIGIN", "http://localhost:5173"),
        "COOKIE_SECURE": "false",
    }
    for name, port in SERVICE_PORTS.items():
        result[f"{name.upper()}_ADDRESS"] = f"127.0.0.1:{port}"

    return result


def stop_processes(processes):
    for process in reversed(processes):
        if process.poll() is None:
            process.terminate()

    for process in processes:
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    env = environment()
    processes = []

    def shutdown(*_):
        raise SystemExit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        for name in SERVICE_PORTS:
            service_env = {
                **env,
                "SERVICE_NAME": name,
                "GRPC_BIND": env[f"{name.upper()}_ADDRESS"],
            }
            process = subprocess.Popen(
                [sys.executable, "-m", "vgm.server"],
                cwd=ROOT,
                env=service_env,
            )
            processes.append(process)

        processes.append(
            subprocess.Popen(
                GATEWAY_COMMAND,
                cwd=ROOT,
                env={
                    **env, "SERVICE_NAME": "gateway"
                },
            )
        )
        print(
            "Backend is starting on http://127.0.0.1:8000. "
            "Run npm run dev in frontend/.",
            flush=True,
        )

        while all(process.poll() is None for process in processes):
            time.sleep(1)

        return 1
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    sys.exit(main())
