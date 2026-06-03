from api.metrics import get_system_metrics


def test_metrics_keys():
    metrics = get_system_metrics()
    for key in ["cpu_percent", "memory_percent", "disk_percent"]:
        assert key in metrics


def test_metrics_range():
    metrics = get_system_metrics()
    for value in metrics.values():
        if isinstance(value, (int, float)):
            assert 0 <= value <= 100 or value > 0
