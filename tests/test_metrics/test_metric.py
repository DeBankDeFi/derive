import unittest
from time import sleep
from pillar.metrics import (
    Counter,
    Summary,
    Gauge,
    Histogram,
)
from pillar.metrics.metric.base import Sample, float_to_string


class MetricTestCase(unittest.TestCase):
    def test_sample(self):
        s = Sample(name="test", labels={}, value=0)
        self.assertEqual("test 0.0", s.data())

        s = Sample(name="test_label", labels=dict(name="test"), value=0)
        self.assertEqual('test_label{name="test"} 0.0', s.data())

    def test_counter(self):
        name = "test"
        document = "Description of counter"
        c = Counter(name, document)
        self.assertEqual(f"# HELP {name}_total {document}", c.help())
        self.assertEqual(f"# TYPE {name}_total counter", c.type())

        c.inc(1)
        samples = list(c.samples())
        self.assertEqual(1, len(samples))
        sample = samples[0]
        self.assertEqual(f"{name}_total", sample.name)
        self.assertEqual(1.0, sample.value)

        with self.assertRaises(Exception):
            with c.count_exceptions():
                raise Exception
        self.assertEqual(2.0, c._count.get())

        with self.assertRaises(Exception):

            @c.count_exceptions()
            def test():
                raise Exception

            test()
        self.assertEqual(3.0, c._count.get())

    def test_gauge(self):
        name = "my_inprogress_requests"
        document = "Description of gauge"
        g = Gauge(name, document)
        self.assertEqual(f"# HELP {name} {document}", g.help())
        self.assertEqual(f"# TYPE {name} gauge", g.type())

        samples = list(g.samples())
        self.assertEqual(1, len(samples))
        count_sample = samples[0]
        self.assertEqual(f"{name}", count_sample.name)
        self.assertEqual(0.0, count_sample.value)

        with g.track_inprogress():
            self.assertEqual(1.0, g._count.get())

        self.assertEqual(0.0, g._count.get())

        @g.track_inprogress()
        def test():
            self.assertEqual(1.0, g._count.get())

        test()
        self.assertEqual(0.0, g._count.get())

        with g.time():
            sleep(1)

        self.assertLessEqual(1.0, g._count.get())

        @g.time()
        def test():
            sleep(1)

        test()
        self.assertLessEqual(1.0, g._count.get())

    def test_summary(self):
        name = "request_size_bytes"
        document = "Request size (bytes)"
        s = Summary(name, document)
        s.observe(512)  # Observe 512 (bytes)
        self.assertEqual(f"# HELP {name} {document}", s.help())
        self.assertEqual(f"# TYPE {name} summary", s.type())

        samples = list(s.samples())
        self.assertEqual(2, len(samples))
        count_sample = samples[0]
        self.assertEqual(f"{name}_count", count_sample.name)
        self.assertEqual(1.0, count_sample.value)
        sum_sample = samples[1]
        self.assertEqual(f"{name}_sum", sum_sample.name)
        self.assertEqual(512.0, sum_sample.value)

        with s.time():
            sleep(1)

        self.assertEqual(2.0, s._count.get())
        self.assertLessEqual(513, s._sum.get())

        @s.time()
        def test():
            sleep(1)

        test()
        self.assertEqual(3.0, s._count.get())
        self.assertLessEqual(513, s._sum.get())

    def test_histogram(self):
        name = "request_size_bytes_h"
        document = "Request size (bytes)"
        h = Histogram(name, document)
        amount = 512
        h.observe(amount)
        self.assertEqual(f"# HELP {name} {document}", h.help())
        self.assertEqual(f"# TYPE {name} histogram", h.type())

        samples = list(h.samples())
        self.assertEqual(len(h.DEFAULT_BUCKETS) + 2, len(samples))

        for i, bound in enumerate(h._upper_bounds):
            if amount <= bound:
                self.assertEqual(1.0, samples[i].value)
                self.assertEqual(
                    f'request_size_bytes_h_bucket{{le="{float_to_string(bound)}"}} 1.0',
                    samples[i].data(),
                )
            else:
                self.assertEqual(
                    f'request_size_bytes_h_bucket{{le="{float_to_string(bound)}"}} 0.0',
                    samples[i].data(),
                )
        count_sample = samples[-2]
        self.assertEqual(f"{name}_count", count_sample.name)
        self.assertEqual(1.0, count_sample.value)
        sum_sample = samples[-1]
        self.assertEqual(f"{name}_sum", sum_sample.name)
        self.assertEqual(512.0, sum_sample.value)

    def test_label(self):
        c = Counter("my_requests_total", "HTTP Failures", {"method", "endpoint"})
        get_counter = c.labels(method="get", endpoint="/")
        get_counter.inc()

        samples = list(get_counter.samples())
        self.assertEqual(1, len(samples))
        sample = samples[0]
        self.assertEqual(
            'my_requests_total_total{endpoint="/",method="get"} 1.0', sample.data()
        )


if __name__ == "__main__":
    unittest.main()
