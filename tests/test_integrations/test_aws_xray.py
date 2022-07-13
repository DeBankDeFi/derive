import sys
import unittest


@unittest.skipIf(sys.platform == "darwin", "Skipping test in os x because of grpc")
class AWSXrayTestCase(unittest.TestCase):
    def test_setup_trace(self):
        from pillar.integrations import aws_xray

        class TestConfig(aws_xray.DefaultConfig):
            ENABLE = True

        aws_xray.Integration(TestConfig()).setup_trace()


if __name__ == "__main__":
    unittest.main()
