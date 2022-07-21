import unittest
from derive import logging


class LoggingTestCase(unittest.TestCase):
    def test_log(self):
        logging.info("test")


if __name__ == "__main__":
    unittest.main()
