from __future__ import unicode_literals

import logging
import os

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def call_send_api(message_data):
    """Makes HTTP requests to Facebook to respond to users: )

    message_data - - a dictionary of the message in messenger's text format
                    including the recipient's ID
    """
    url = settings.FACEBOOK_MESSAGES_URL
    params = {
        'access_token': os.getenv('PAGE_ACCESS_TOKEN')
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, params=params,
                             headers=headers, json=message_data)

    if response.status_code == 200:
        logger.info({
            'msg': 'Response successfully sent',
            'message_data': message_data,
            'type': 'call_send_api_successful'
        })
    else:
        logger.warning({
            'msg': 'Sending response failed!!!',
            'message_data': message_data,
            'response': response.json(),
            'type': 'call_send_api_unsuccessful'
        })


def fetch_users_first_name(sender_id):
    """Fetch user's first_name from Facebook"""
    url = '{base_url}/{PSID}'.format(
        base_url=settings.FACEBOOK_BASE_URL, PSID=sender_id)
    params = {
        'fields': 'first_name',
        'access_token': os.getenv('PAGE_ACCESS_TOKEN')
    }
    response = requests.get(url, params)

    if response.status_code == 200:
        first_name = response.json()['first_name']
        return first_name
    else:
        logger.warning({
            'msg': 'Sending response failed!!!',
            'sender_id': sender_id,
            'response': response.json(),
            'type': 'fetch_users_first_name_failed'
        })
        return ''
