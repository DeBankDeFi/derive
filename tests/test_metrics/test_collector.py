import unittest
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


from pillar.metrics.metric import Counter
from pillar.metrics.collector import GlobalCollector

name = "test_collector"
document = "Description of counter"
counter = Counter(name, document)


def thread_task(_):
    Counter(name, document).inc(1)


def process_task(_):
    with ThreadPoolExecutor() as worker:
        worker.map(thread_task, range(2))
        worker.map(thread_task, range(2))


class CollectorTestCase(unittest.TestCase):
    def test_concurrent(self):
        with ProcessPoolExecutor() as worker:
            worker.map(process_task, range(2))
            worker.map(process_task, range(2))

        self.assertEqual(f"{name}_total 16.0", list(counter.samples())[0].data())

    def test_register(self):
        temp_counter = Counter(name, document)
        self.assertEqual(1, len(list(GlobalCollector.collect())))


if __name__ == "__main__":
    unittest.main()
