import mock
from unittest import TestCase

from messager.decorators import log_received_event


class LogReceivedEventTest(TestCase):

    @mock.patch('messager.decorators.logger.info')
    def test_logs_generated(self, mock_logger):
        event = {'type': 'cool event'}

        def func(event):
            return event

        result = log_received_event(func)(event)
        mock_logger.assert_called_once_with(dict(
            msg='Received request',
            event=event,
            type='webhook_received_request'
        ))
