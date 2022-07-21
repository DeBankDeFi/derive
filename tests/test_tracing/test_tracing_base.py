import unittest

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import INVALID_SPAN

from pillar.trace import trace, set_provider
from tests import async_test


class TracingBaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        set_provider(TracerProvider())

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
            self.assertIsNotNone(trace.get_current_span())

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
