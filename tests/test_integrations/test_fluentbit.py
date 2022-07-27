import unittest
from unittest import mock

from derive import logging
from derive.integrations import fluentbit


class FluentBitTestCase(unittest.TestCase):
    old_root: logging.DeriveLogger

    def setUp(self):
        self.old_root = logging.root

    def tearDown(self):
        logging.root = self.old_root

    def test_logging(self):
        with mock.patch("socket.create_connection") as m_create_connection:
            m_sendall = mock.MagicMock()
            conn = mock.MagicMock(sendall=m_sendall)
            conn.__enter__ = mock.MagicMock(return_value=conn)
            conn.__exit__ = mock.MagicMock(return_value=False)
            m_create_connection.return_value = conn
            config = fluentbit.DefaultConfig()
            config.ENABLE = True
            integration = fluentbit.Integration(config)
            integration.setup()
            logging.info("test")
            integration.handler.flush()
            self.assertFalse(integration.handler.listener.is_alive)
            m_create_connection.assert_called_once_with(
                (config.TCP_HOST, config.TCP_PORT), 0.5
            )
            m_sendall.assert_called_once()


if __name__ == "__main__":
    unittest.main()
