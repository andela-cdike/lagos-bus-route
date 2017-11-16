from __future__ import unicode_literals

import logging
import os

import requests


logger = logging.getLogger(__name__)


def call_send_api(message_data):
    """Makes HTTP requests to Facebook to respond to users: )

    message_data - - a dictionary of the message in messenger's text format
                    including the recipient's ID
    """
    url = 'https://graph.facebook.com/v2.6/me/messages'
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
    url = 'https://graph.facebook.com/v2.6/{PSID}'.format(PSID=sender_id)
    params = {
        'fields': 'first_name',
        'access_token': os.getenv('PAGE_ACCESS_TOKEN')
    }
    response = requests.get(url, params).json()
    first_name = response['first_name']
    return first_name
