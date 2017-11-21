# from __future__ import unicode_literals

import datetime
import json
import os
from mock import ANY, patch

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils.http import urlencode

from messager import request_processor
from messager.tests import testing_utils


class WebhookViewTest(TestCase):
    POSTBACK = 'postback'
    MESSAGE = 'message'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        try:
            self.mock_call_send_api_patch.stop()
            self.mock_fetch_users_first_name_patch.stop()
        except AttributeError:
            pass

    def setup_call_api_for_success(self):
        self.sender_id = 'sender_id'
        self.mock_call_send_api_patch = patch(
            'messager.messengers.call_send_api')
        self.mock_call_send_api = self.mock_call_send_api_patch.start()
        self.response = testing_utils.Response(200)
        self.mock_call_send_api.return_value = self.response

        self.mock_fetch_users_first_name_patch = patch(
            'messager.request_processor.fetch_users_first_name')
        self.mock_fetch_users_first_name = self.mock_fetch_users_first_name_patch.start()
        self.mock_fetch_users_first_name.return_value = 'test_user'

    def test_successful_verify_webhook(self):
        params = urlencode({
            'hub.mode': 'subscribe',
            'hub.challenge': 'tough_challenge',
            'hub.verify_token': os.getenv('VERIFY_TOKEN')
        })
        response = self.client.get('{base_url}?{params}'.format(
            base_url=reverse('webhook'), params=params))
        self.assertEqual(response.status_code, 200)

    def test_webhook_with_mode_other_than_subscribe(self):
        params = urlencode({
            'hub.mode': 'some_other_mode',
            'hub.challenge': 'tough_challenge',
            'hub.verify_token': os.getenv('VERIFY_TOKEN')
        })
        response = self.client.get('{base_url}?{params}'.format(
            base_url=reverse('webhook'), params=params))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         "Don't know how to deal with this yet")

    def test_webhook_with_no_challenge(self):
        params = urlencode({
            'hub.mode': 'some_other_mode',
            'hub.verify_token': os.getenv('VERIFY_TOKEN')
        })
        response = self.client.get('{base_url}?{params}'.format(
            base_url=reverse('webhook'), params=params))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         "Don't know how to deal with this yet")

    def test_webhook_with_invalid_verify_token(self):
        params = urlencode({
            'hub.mode': 'subscribe',
            'hub.challenge': 'tough_challenge',
            'hub.verify_token': 'invalid_verify_token'
        })
        response = self.client.get('{base_url}?{params}'.format(
            base_url=reverse('webhook'), params=params))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'Verification token mismatch')

    def create_messaging_data(self, type=None):
        data = {
            'object': 'page',
            'entry': [
                {
                    'id': '1',
                    'time': unicode(datetime.datetime.now()),
                    'messaging': [
                        {
                            'sender': {'id': 'sender_id'},
                        }
                    ]
                }
            ]
        }
        if type == self.MESSAGE:
            data['entry'][0]['messaging'][0][self.MESSAGE] = {
                'text': 'shita, surulere; cms, lagos island',
                'attachments': None
            }
        elif type == self.POSTBACK:
            data['entry'][0]['messaging'][0][self.POSTBACK] = {
                'payload': 'GET_STARTED_PAYLOAD'
            }
        else:
            data['entry'][0]['messaging'][0]['invalid_event'] = {
                'payload': 'random long string'
            }
        return data

    def test_send_valid_postback_to_webhook(self):
        data = self.create_messaging_data(self.POSTBACK)
        self.setup_call_api_for_success()
        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.mock_call_send_api.assert_called_once()
        self.assertIn(self.sender_id, call_send_api_arg)

    def test_send_invalid_postback_to_webhook(self):
        data = self.create_messaging_data(self.POSTBACK)
        data['entry'][0]['messaging'][0][self.POSTBACK] = {
            'payload': 'SOME_INVALID_POSTBACK'
        }
        self.setup_call_api_for_success()

        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.mock_call_send_api.assert_called_once()
        self.assertIn(self.sender_id, call_send_api_arg)
        self.assertIn('invalid postback', call_send_api_arg)

    @patch('messager.views.logger.warning')
    def test_invalid_event_type(self, mock_logger):
        data = self.create_messaging_data()
        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        mock_logger.assert_called_once_with(dict(
            msg=ANY, event=data['entry'][0]['messaging'][0],
            type='webhook_unknown_event'
        ))

    def test_send_help_message(self):
        """Expect three calls to the facebook messenger endpoint:
         - typing action
         - a return greeting
         - instruction message
        """
        data = self.create_messaging_data(self.MESSAGE)
        data['entry'][0]['messaging'][0][self.MESSAGE]['text'] = 'help'
        self.setup_call_api_for_success()

        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.mock_call_send_api.call_count, 3)

    def test_send_greeting_message(self):
        """Expect three calls to the facebook messenger endpoint:
         - typing action
         - a return greeting
         - instruction message
        """
        data = self.create_messaging_data(self.MESSAGE)
        data['entry'][0]['messaging'][0][self.MESSAGE]['text'] = 'Hi'
        self.setup_call_api_for_success()

        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.mock_call_send_api.call_count, 3)

    def test_send_message_with_attachment(self):
        data = self.create_messaging_data(self.MESSAGE)
        data['entry'][0]['messaging'][0][self.MESSAGE]['text'] = ''
        data['entry'][0]['messaging'][0][self.MESSAGE]['attachments'] = 'some img/video/audio attachment'
        self.setup_call_api_for_success()

        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.mock_call_send_api.call_count, 2)

        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.assertIn("don't support attachments", call_send_api_arg)

    def test_send_message_with_text(self):
        data = self.create_messaging_data(self.MESSAGE)
        self.setup_call_api_for_success()

        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @patch('messager.views.logger.error')
    @patch('messager.views.handle_message', side_effect=TypeError('Failed!!'))
    def test_send_message_and_unexpected_exception_occurs(self, _, mock_logger):
        data = self.create_messaging_data(self.MESSAGE)
        self.setup_call_api_for_success()

        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # facebook messenger api is called once with the error message
        self.assertEqual(self.mock_call_send_api.call_count, 1)

        mock_logger.assert_called_once_with(dict(
            msg=ANY, event=data['entry'][0]['messaging'][0],
            error=ANY, type='unhandled_handle_message_exception'
        ))

        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.assertIn('Please try again', call_send_api_arg)

    @patch('messager.decorators.logger.info')
    def test_log_event_when_receives_text_message(self, mock_logger):
        data = self.create_messaging_data(self.MESSAGE)
        self.setup_call_api_for_success()

        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        mock_logger.assert_called_once_with(dict(
            msg='Received request',
            event=data['entry'][0]['messaging'][0],
            type='webhook_received_request'
        ))

    @patch('messager.decorators.logger.info')
    def test_log_event_when_receives_postback_message(self, mock_logger):
        data = self.create_messaging_data(self.POSTBACK)
        self.setup_call_api_for_success()

        response = self.client.post(reverse('webhook'),
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        mock_logger.assert_called_once_with(dict(
            msg='Received request',
            event=data['entry'][0]['messaging'][0],
            type='webhook_received_request'
        ))
