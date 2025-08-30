import logging

def monitor_memory_usage(threshold_mb=800):
    """
    Surveille l'utilisation mémoire du processus courant et log un avertissement si le seuil est dépassé.
    Args:
        threshold_mb (int): Seuil en mégaoctets (MB)
    Returns:
        bool: True si sous le seuil, False sinon
    """
    try:
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        if memory_usage > threshold_mb:
            logging.warning(f"Utilisation mémoire élevée: {memory_usage:.2f}MB")
            return False
        return True
    except Exception as e:
        logging.error(f"Erreur monitor_memory_usage: {e}")
        return True
import time
import tracemalloc
from contextlib import contextmanager

class PerformanceMonitor:
    def __init__(self):
        self.snapshots = {}
        tracemalloc.start()

    @contextmanager
    def track_performance(self, task_name):
        start_time = time.time()
        start_mem = tracemalloc.take_snapshot()
        yield
        end_time = time.time()
        end_mem = tracemalloc.take_snapshot()
        stats = {
            "duration": end_time - start_time,
            "memory_diff": end_mem.compare_to(start_mem, 'lineno')
        }
        self.snapshots[task_name] = stats

    def generate_report(self):
        report = "Performance Report:\n"
        for task, stats in self.snapshots.items():
            report += f"\n[{task}]\n"
            report += f"  Duration: {stats['duration']:.2f}s\n"
            report += "  Memory Changes:\n"
            for diff in stats['memory_diff'][:5]:
                report += f"    {diff}\n"
        return report
