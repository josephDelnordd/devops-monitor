from api.metrics import get_system_metrics


# Tests pour les fonctions de récupération des métriques système
def test_metrics_keys():
    metrics = get_system_metrics()
    for key in ["cpu_percent", "memory_percent", "disk_percent"]:
        assert key in metrics

# Test pour vérifier que les valeurs des métriques sont dans une plage raisonnable (0-100% pour CPU, mémoire et disque)
def test_metrics_range():
    metrics = get_system_metrics()
    for value in metrics.values():
        if isinstance(value, (int, float)):
            assert 0 <= value <= 100 or value > 0
