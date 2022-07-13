import unittest

from pillar.trace import trace, set_tracer
from tests import async_test
from opentelemetry.trace import INVALID_SPAN


from opentelemetry import trace as opentelemetry_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_OFF,
)
from opentelemetry.trace.span import SpanContext, Span
from opentelemetry.util import types


class TracingBaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        provider = TracerProvider()
        opentelemetry_trace.set_tracer_provider(provider)
        set_tracer(provider.get_tracer("test"))

    @classmethod
    def tearDownClass(cls) -> None:
        set_tracer(opentelemetry_trace.NoOpTracer())

    def test_sync_context(self):
        with trace("parent") as parent_span:
            self.assertEqual(
                parent_span.get_span_context().span_id,
                trace.get_current_span_context().span_id,
            )
            with trace("child") as child_span:
                self.assertEqual(
                    child_span.get_span_context().span_id,
                    trace.get_current_span_context().span_id,
                )
                self.assertEqual(
                    parent_span.get_span_context().span_id, child_span.parent.span_id
                )

    def test_sync_decorator(self):
        @trace("test")
        def test():
            self.assertIsNot(INVALID_SPAN, trace.get_current_span())

        test()

    @async_test
    async def test_async_context(self):
        with trace("parent") as parent_span:
            self.assertIsNot(INVALID_SPAN, trace.get_current_span())
            with trace("child") as child_span:
                self.assertIs(
                    trace.get_current_span_context().span_id,
                    child_span.get_span_context().span_id,
                )
                self.assertEqual(
                    parent_span.get_span_context().span_id, child_span.parent.span_id
                )

    @async_test
    async def test_async_decorator(self):
        @trace("parent")
        async def async_func():
            parent_span = trace.get_current_span()
            self.assertIsNot(INVALID_SPAN, parent_span)
            with trace("child") as child_span:
                self.assertIs(
                    trace.get_current_span_context().span_id,
                    child_span.get_span_context().span_id,
                )
                self.assertEqual(
                    parent_span.get_span_context().span_id, child_span.parent.span_id
                )

        await async_func()


if __name__ == "__main__":
    unittest.main()
