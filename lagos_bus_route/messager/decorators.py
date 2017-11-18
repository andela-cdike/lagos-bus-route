from __future__ import unicode_literals

import functools
import logging


logger = logging.getLogger(__name__)


def log_received_event(func):
    """Logs received events"""
    @functools.wraps(func)
    def wrapper(event):
        """Log then call the handler proper"""
        logger.info({
            'msg': 'Received request',
            'event': event,
            'type': 'webhook_received_request'
        })

        result = func(event)
        return result
    return wrapper
