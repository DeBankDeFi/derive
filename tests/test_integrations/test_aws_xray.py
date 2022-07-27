import unittest

from opentelemetry.sdk import resources

import derive
from derive.integrations import aws_xray
from derive.trace import get_tracer


class Config(aws_xray.DefaultConfig):
    ENABLE = True


class AWSXrayTestCase(unittest.TestCase):
    def test_setup_trace(self):
        derive_config = derive.DefaultConfig()
        derive.init(derive_config)
        aws_xray.Integration(Config()).setup()
        tracer = get_tracer()
        resource: resources.Resource = getattr(tracer, "resource")
        self.assertIsNotNone(resource)
        self.assertEqual(
            resource.attributes[resources.SERVICE_NAME], derive_config.SERVICE_NAME
        )


if __name__ == "__main__":
    unittest.main()
