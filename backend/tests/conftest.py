import os
import pathlib
import socket
import subprocess
import sys

import grpc
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def gateway():
    database = os.getenv("TEST_DATABASE_URL")
    if not database:
        pytest.skip(
            "Set TEST_DATABASE_URL to a dedicated PostgreSQL test database"
        )
    os.environ["DATABASE_URL"] = database
    os.environ["PUBLIC_ORIGIN"] = "http://localhost:8080"
    os.environ["COOKIE_SECURE"] = "false"
    os.environ.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
    subprocess.run(
        [
            sys.executable, "-m", "alembic", "-c", "backend/alembic.ini",
            "upgrade", "head"
        ],
        cwd=ROOT,
        check=True
    )
    processes, logs = [], []
    for name in ("identity", "video", "messaging"):
        os.environ[f"{name.upper()}_ADDRESS"] = f"127.0.0.1:{free_port()}"
    try:
        (ROOT / "work").mkdir(exist_ok=True)
        for name in ("identity", "video", "messaging"):
            address = os.environ[f"{name.upper()}_ADDRESS"]
            env = {
                **os.environ, "SERVICE_NAME": name,
                "GRPC_BIND": address,
                "PYTHONPATH": str(ROOT / "backend")
            }
            log = (ROOT / "work" / f"test-{name}.log").open("w")
            logs.append(log)
            processes.append(
                subprocess.Popen(
                    [sys.executable, "-m", "vgm.server"],
                    env=env,
                    cwd=ROOT,
                    stdout=log,
                    stderr=log
                )
            )
            with grpc.insecure_channel(address) as channel:
                grpc.channel_ready_future(channel).result(timeout=20)
        from vgm import gateway
        gateway.app.config["TESTING"] = True
        yield gateway.app
    finally:
        for process in reversed(processes):
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for log in logs:
            log.close()


@pytest.fixture(autouse=True)
def clear_rate_limiter():
    if "vgm.gateway" in sys.modules:
        sys.modules["vgm.gateway"].attempts.clear()
