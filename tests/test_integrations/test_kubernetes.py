import os
import unittest

from opentelemetry.sdk import resources

from derive.integrations import kubernetes
from derive.trace import get_tracer


class KubernetesTestCase(unittest.TestCase):
    def test_setup(self):
        os.environ["K8S_CLUSTER_NAME"] = "test"
        kubernetes.Integration().setup()
        tracer = get_tracer()
        resource: resources.Resource = getattr(tracer, "resource")
        self.assertIsNotNone(resource)
        self.assertEqual(resource.attributes[resources.KUBERNETES_CLUSTER_NAME], "test")


if __name__ == "__main__":
    unittest.main()
