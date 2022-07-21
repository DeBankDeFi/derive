import unittest
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from derive.metrics.manager import manager

v = manager.MetricValue()


def thread_task(_):
    v.inc(1)


def process_task(_):
    with ThreadPoolExecutor() as worker:
        worker.map(thread_task, range(2))
        worker.map(thread_task, range(2))


class MutexValueTestCase(unittest.TestCase):
    def test_concurrent(self):
        with ProcessPoolExecutor() as worker:
            worker.map(process_task, range(4))

        self.assertEqual(2**4, v.get())


if __name__ == "__main__":
    unittest.main()
