import collections
from mock import ANY, patch
from unittest import TestCase

from messager import facebook_requests
from messager.tests import testing_utils


class FacebookRequestsTest(TestCase):
    @patch('messager.facebook_requests.logger.info')
    @patch('messager.facebook_requests.requests.post')
    def test_call_send_api_success(self, mock_requests_post, mock_logger):
        mock_requests_post.return_value = testing_utils.Response(200)
        message_data = 'Welcome to the lagos bus route app'
        facebook_requests.call_send_api(message_data)
        mock_requests_post.assert_called_once()
        mock_logger.assert_called_once_with({
            'type': 'call_send_api_successful', 'message_data': message_data, 'msg': ANY})

    @patch('messager.facebook_requests.logger.warning')
    @patch('messager.facebook_requests.requests.post')
    def test_call_send_api_error(self, mock_requests_post, mock_logger):
        mocked_response = testing_utils.Response(403)
        mock_requests_post.return_value = mocked_response
        message_data = 'Welcome to the lagos bus route app'
        facebook_requests.call_send_api(message_data)
        mock_requests_post.assert_called_once()
        mock_logger.assert_called_once_with({
            'type': 'call_send_api_unsuccessful', 'message_data': message_data,
            'response': ANY, 'msg': ANY})

    @patch('messager.facebook_requests.requests.get')
    def test_call_fetch_users_first_name_successful(self, mock_requests_get):
        response = testing_utils.Response(200, 'test_user')
        mock_requests_get.return_value = response
        sender_id = 'sender_id'
        first_name = facebook_requests.fetch_users_first_name(sender_id)
        self.assertEqual(first_name, response.first_name)

    @patch('messager.facebook_requests.logger.warning')
    @patch('messager.facebook_requests.requests.get')
    def test_call_fetch_users_first_name_error(self, mock_requests_get, mock_logger):
        response = testing_utils.Response(400, 'test_user')
        mock_requests_get.return_value = response
        sender_id = 'sender_id'
        first_name = facebook_requests.fetch_users_first_name(sender_id)
        self.assertEqual(first_name, '')
        mock_logger.assert_called_once_with(dict(
            msg=ANY, sender_id=sender_id, response=response.json(),
            type='fetch_users_first_name_failed'
        ))
