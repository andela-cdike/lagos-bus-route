from mock import patch
from unittest import TestCase

from messager import messengers


class MessengersTests(TestCase):
    @patch('messager.messengers.call_send_api')
    def test_send_text_message(self, mock_call_send_api):
        recipient_id = 'recipient_id'
        message = 'I give the best directions'
        messengers.send_text_message(recipient_id, message)
        mock_call_send_api.assert_called_once()

    @patch('messager.messengers.call_send_api')
    def test_send_typing_action(self, mock_call_send_api):
        recipient_id = 'recipient_id'
        messengers.send_typing_action(recipient_id)
        mock_call_send_api.assert_called_once()

    @patch('messager.messengers.call_send_api')
    def test_send_instructions(self, mock_call_send_api):
        recipient_id = 'recipient_id'
        messengers.send_instructions(recipient_id)
        mock_call_send_api.assert_called_once()

    @patch('messager.messengers.call_send_api')
    def test_send_one_route(self, mock_call_send_api):
        recipient_id = 'recipient_id'
        routes = ['lawanson -> ogunlana -> ojuelegba']
        messengers.send_routes(recipient_id, routes)
        mock_call_send_api.assert_called_once()

    @patch('messager.messengers.call_send_api')
    def test_send_double_routes(self, mock_call_send_api):
        recipient_id = 'recipient_id'
        routes = ['lawanson -> ogunlana -> ojuelegba',
                  'lawanson -> mushin -> ilasa']
        messengers.send_routes(recipient_id, routes)
        self.assertEqual(mock_call_send_api.call_count, 2)
