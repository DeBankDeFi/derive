import unittest

from pillar.integrations import aws_xray


class Config(aws_xray.DefaultConfig):
    ENABLE = True


class AWSXrayTestCase(unittest.TestCase):
    def test_setup_trace(self):
        aws_xray.Integration(Config()).setup_trace()


if __name__ == "__main__":
    unittest.main()
