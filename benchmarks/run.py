"""Run matched local HTTP benchmarks and retain every hey measurement."""
import argparse
from contextlib import contextmanager
from datetime import datetime
from datetime import timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import re
import shutil
import socket
import statistics
import subprocess
import sys
import time
from urllib.request import Request
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "text": ("/text", "GET", None, b"Hello, world!"),
    "typed": ("/users/42?active=false&limit=20", "GET", None, b"42:False:20"),
    "context": ("/context", "GET", None, b"benchmark:dark"),
    "body": ("/body", "POST", b"x" * 1024, b"x" * 1024),
}
HEADERS = {"X-Client": "benchmark", "Cookie": "theme=dark"}


def output(command):
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def parse_measurement(raw):
    def number(pattern):
        match = re.search(pattern, raw)
        if not match:
            raise RuntimeError(f"Missing hey metric: {pattern}\n{raw}")
        return float(match[1])

    statuses = {code: int(count) for code, count in re.findall(r"\[(\d{3})\]\s+(\d+) responses", raw)}
    if not statuses or set(statuses) != {"200"} or "Error distribution:" in raw:
        raise RuntimeError(f"Benchmark had failed requests:\n{raw}")
    return {
        "requests_per_second": number(r"Requests/sec:\s+([\d.]+)"),
        "mean_ms": 1000 * number(r"Average:\s+([\d.]+) secs"),
        "p95_ms": 1000 * number(r"95%+ in ([\d.]+) secs"),
        "p99_ms": 1000 * number(r"99%+ in ([\d.]+) secs"),
        "elapsed_seconds": number(r"Total:\s+([\d.]+) secs"),
        "status_counts": statuses,
        "errors": 0,
    }


@contextmanager
def server(framework, log_path):
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join([str(ROOT / "src"), str(ROOT)])
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(128)
        port = listener.getsockname()[1]
        command = [
            sys.executable, "-m", "uvicorn", f"benchmarks.apps:{framework}_app",
            "--fd", str(listener.fileno()), "--workers", "1", "--loop", "asyncio",
            "--http", "h11", "--lifespan", "on", "--no-access-log",
            "--no-server-header", "--no-date-header", "--log-level", "warning",
        ]
        with log_path.open("w") as log:
            process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=log, stderr=log,
                                       pass_fds=(listener.fileno(),))
            try:
                deadline = time.monotonic() + 20
                while True:
                    if process.poll() is not None:
                        raise RuntimeError(f"Server exited: {log_path.read_text()}")
                    try:
                        with urlopen(f"http://127.0.0.1:{port}/text", timeout=0.3) as response:
                            if response.status == 200:
                                break
                    except OSError:
                        if time.monotonic() >= deadline:
                            raise RuntimeError(f"Server did not start: {log_path.read_text()}")
                        time.sleep(0.05)
                yield f"http://127.0.0.1:{port}", command
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--concurrency", type=int, nargs="+", default=[1, 32])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if min(args.seconds, args.warmup, args.repeats, *args.concurrency) < 1:
        parser.error("durations, repeats, and concurrency must be positive")
    hey = shutil.which("hey")
    if not hey:
        parser.error("Install hey and put it on PATH (macOS: brew install hey)")
    args.output.mkdir(parents=True, exist_ok=False)
    files = [*sorted((ROOT / "src/karak").rglob("*.py")),
             Path(__file__).resolve(), ROOT / "benchmarks/apps.py", ROOT / "benchmarks/uv.lock"]
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    report = {
        "metadata": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
            "cpu": output(["sysctl", "-n", "machdep.cpu.brand_string"]) if sys.platform == "darwin" else platform.processor(),
            "logical_cpus": os.cpu_count(),
            "versions": {package: version(package) for package in ("fastapi", "starlette", "pydantic", "uvicorn", "h11")},
            "hey_sha256": hashlib.sha256(Path(hey).read_bytes()).hexdigest(),
            "git_commit": output(["git", "rev-parse", "HEAD"]),
            "git_status": output(["git", "status", "--short"]),
            "source_sha256": hashes,
            "seconds": args.seconds, "warmup_seconds": args.warmup, "repeats": args.repeats,
            "concurrency": args.concurrency, "hey_cpus": 2,
            "server": "Uvicorn, 1 worker, asyncio, h11, lifespan on, access logs off",
            "transport": "HTTP/1.1, keep-alive, loopback; client and server on same host",
        },
        "runs": [],
    }
    for repetition in range(1, args.repeats + 1):
        frameworks = ("karak", "fastapi") if repetition % 2 else ("fastapi", "karak")
        for case, (path, method, body, expected) in CASES.items():
            for concurrency in args.concurrency:
                for framework in frameworks:
                    label = f"{case}-c{concurrency}-{framework}-r{repetition}"
                    with server(framework, args.output / f"{label}.server.log") as (base, server_command):
                        req = Request(base + path, data=body, headers=HEADERS, method=method)
                        with urlopen(req, timeout=5) as response:
                            assert response.status == 200
                            assert response.read() == expected, label
                            assert response.headers["content-type"] == "text/plain; charset=utf-8", label
                            assert response.headers["content-length"] == str(len(expected)), label
                        command = [hey, "-c", str(concurrency), "-cpus", "2", "-t", "10", "-m", method]
                        for name, value in HEADERS.items():
                            command.extend(["-H", f"{name}: {value}"])
                        if body:
                            command.extend(["-d", body.decode()])
                        warmup = subprocess.run([*command, "-z", f"{args.warmup}s", base + path],
                                                capture_output=True, text=True, check=True, timeout=args.warmup + 20)
                        parse_measurement(warmup.stdout)
                        measured_command = [*command, "-z", f"{args.seconds}s", base + path]
                        measured = subprocess.run(measured_command, capture_output=True, text=True,
                                                  check=True, timeout=args.seconds + 20)
                        (args.output / f"{label}.txt").write_text(measured.stdout)
                        metrics = parse_measurement(measured.stdout)
                        report["runs"].append({"framework": framework, "case": case, "concurrency": concurrency,
                                               "repetition": repetition, "command": measured_command,
                                               "server_command": server_command, **metrics})
                        (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
                        print(f"{label}: {metrics['requests_per_second']:.0f} req/s, p95={metrics['p95_ms']:.2f} ms", flush=True)
    changed = [name for name, digest in hashes.items() if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    if changed:
        raise RuntimeError(f"Sources changed during measurement; discard this run: {changed}")
    report["metadata"]["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    report["summary"] = []
    for case in CASES:
        for concurrency in args.concurrency:
            for framework in ("karak", "fastapi"):
                rows = [row for row in report["runs"] if (row["case"], row["concurrency"], row["framework"]) == (case, concurrency, framework)]
                rates = [row["requests_per_second"] for row in rows]
                report["summary"].append({
                    "case": case, "concurrency": concurrency, "framework": framework,
                    "median_rps": statistics.median(rates), "min_rps": min(rates), "max_rps": max(rates),
                    "median_p95_ms": statistics.median(row["p95_ms"] for row in rows),
                    "median_p99_ms": statistics.median(row["p99_ms"] for row in rows),
                    "requests": sum(row["status_counts"]["200"] for row in rows), "errors": 0,
                })
    (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Complete: {args.output / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
