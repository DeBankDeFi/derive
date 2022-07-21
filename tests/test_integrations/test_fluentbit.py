import unittest
from unittest import mock

import pillar
from pillar import logging
from pillar.integrations import fluentbit


class FluentBitTestCase(unittest.TestCase):
    old_root: logging.PillarLogger

    def setUp(self):
        self.old_root = logging.root

    def tearDown(self):
        logging.root = self.old_root

    def test_logging(self):
        with mock.patch("socket.create_connection") as m_create_connection:
            m_sendall = mock.MagicMock()
            conn = mock.MagicMock(sendall=m_sendall)
            m_create_connection.return_value = conn
            config = fluentbit.DefaultConfig()
            config.ENABLE = True
            fluentbit.Integration(config, pillar.DefaultConfig()).setup_logging()
            logging.info("test")
            handler: fluentbit.FluentBitLoggingQueueHandler = logging.root.handlers[1]
            self.assertIsInstance(handler, fluentbit.FluentBitLoggingQueueHandler)
            handler.flush()
            self.assertFalse(handler.listener.is_alive)
            m_create_connection.assert_called_once_with(
                (config.TCP_HOST, config.TCP_PORT), 0.5
            )
            m_sendall.assert_called_once()


if __name__ == "__main__":
    unittest.main()
