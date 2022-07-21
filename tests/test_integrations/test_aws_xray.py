import unittest

from opentelemetry.sdk import resources

import pillar
from pillar.integrations import aws_xray
from pillar.trace import get_tracer


class Config(aws_xray.DefaultConfig):
    ENABLE = True


class AWSXrayTestCase(unittest.TestCase):
    def test_setup_trace(self):
        pillar_config = pillar.DefaultConfig()
        aws_xray.Integration(Config(), pillar_config).setup_trace()
        tracer = get_tracer()
        resource: resources.Resource = getattr(tracer, "resource")
        self.assertIsNotNone(resource)
        self.assertEqual(
            resource.attributes[resources.SERVICE_NAME], pillar_config.SERVICE_NAME
        )


if __name__ == "__main__":
    unittest.main()
