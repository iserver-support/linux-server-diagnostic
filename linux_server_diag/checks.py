import os
import shutil
import socket
import subprocess
from pathlib import Path


def run_command(command):
    """Run a system command and return its output.

    Commands are executed without a shell so user-controlled input cannot
    accidentally become shell syntax.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)

    if result.returncode != 0:
        return None, result.stderr.strip()

    return result.stdout.strip(), None


def check_system():
    """Collect basic system information."""
    result = {}

    result["hostname"] = socket.gethostname()

    try:
        result["load_average"] = os.getloadavg()
    except OSError:
        result["load_average"] = None

    result["cpu_count"] = os.cpu_count() or 0

    uptime, error = run_command(["uptime", "-p"])
    result["uptime"] = uptime if not error else "unavailable"

    return result


def check_memory():
    """Read memory information from /proc/meminfo."""
    meminfo = Path("/proc/meminfo")

    if not meminfo.exists():
        return {"error": "This system does not expose /proc/meminfo"}

    values = {}

    try:
        for line in meminfo.read_text().splitlines():
            key, value = line.split(":", 1)
            parts = value.strip().split()

            if parts and parts[0].isdigit():
                values[key] = int(parts[0])
    except (OSError, ValueError):
        return {"error": "Unable to read /proc/meminfo"}

    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", 0)

    if total:
        used_percent = ((total - available) / total) * 100
    else:
        used_percent = 0

    return {
        "total_mb": round(total / 1024, 2),
        "available_mb": round(available / 1024, 2),
        "used_percent": round(used_percent, 2),
        "swap_total_mb": round(values.get("SwapTotal", 0) / 1024, 2),
        "swap_free_mb": round(values.get("SwapFree", 0) / 1024, 2),
    }


def check_filesystem(path="/"):
    """Check filesystem space and inode availability."""
    try:
        usage = shutil.disk_usage(path)
    except OSError as exc:
        return {"path": path, "error": str(exc)}

    used_percent = (usage.used / usage.total) * 100

    stat = os.statvfs(path)

    total_inodes = stat.f_files
    free_inodes = stat.f_ffree

    inode_percent = (
        ((total_inodes - free_inodes) / total_inodes) * 100
        if total_inodes
        else 0
    )

    return {
        "path": path,
        "size_gb": round(usage.total / 1024**3, 2),
        "used_gb": round(usage.used / 1024**3, 2),
        "free_gb": round(usage.free / 1024**3, 2),
        "used_percent": round(used_percent, 2),
        "inode_used_percent": round(inode_percent, 2),
    }


def check_failed_services():
    """Return failed systemd units when systemd is available."""
    output, error = run_command(
        ["systemctl", "--failed", "--no-legend", "--plain"]
    )

    if error:
        return {
            "available": False,
            "reason": error,
        }

    services = [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]

    return {
        "available": True,
        "failed_count": len(services),
        "services": services,
    }


def check_listening_ports():
    """Return listening TCP/UDP sockets using ss."""
    output, error = run_command(
        ["ss", "-lntuH"]
    )

    if error:
        return {
            "available": False,
            "reason": error,
        }

    return {
        "available": True,
        "sockets": output.splitlines(),
    }
