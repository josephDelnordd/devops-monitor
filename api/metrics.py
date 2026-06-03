import psutil
from typing import Dict


def get_system_metrics() -> Dict[str, float]:
    """Return a snapshot of system metrics."""
    cpu = psutil.cpu_percent(interval=None)

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "memory_used_gb": round(mem.used / (1024 ** 3), 2),
        "disk_percent": disk.percent,
    }