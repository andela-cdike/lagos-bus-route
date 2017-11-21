from __future__ import unicode_literals

from mock import ANY, patch
from unittest import TestCase

from busstops.busstop_processor import BusstopProcessor
from busstops.exceptions import BusStopNotFoundException
from factories.factories import BusStopFactory
from routes.route_engine import RouteEngine
from routes.exceptions import NoRouteFoundException

from messager import request_processor
from messager.exceptions import FormatException
from messager.tests import testing_utils


class RequestProcessorTest(TestCase):
    def setUp(self):
        self.sender_id = 'sender_id'
        self.mock_call_send_api_patch = patch(
            'messager.messengers.call_send_api')
        self.mock_call_send_api = self.mock_call_send_api_patch.start()

    def tearDown(self):
        self.mock_call_send_api_patch.stop()

    def setup_call_api_for_success(self):
        self.response = testing_utils.Response(200)
        self.mock_call_send_api.return_value = self.response

    def setupCallApiForFailure(self):
        self.response = testing_utils.Response(400)
        self.mock_call_send_api.return_value = self.response

    def test_notify_about_other_busstops_if_required_two_other_busstops(self):
        self.setup_call_api_for_success()
        location = 'ogunlana drive'
        other_busstops = ['masha', 'shita']
        request_processor.notify_about_other_busstops_if_required(
            location, other_busstops, self.sender_id)
        self.mock_call_send_api.assert_called_once()
        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.assertIn(self.sender_id, call_send_api_arg)
        self.assertIn(location, call_send_api_arg)
        for busstop in other_busstops:
            self.assertIn(busstop, call_send_api_arg)

    def test_notify_about_other_busstops_if_required_empty_other_busstops(self):
        self.setup_call_api_for_success()
        location = 'ogunlana drive'
        other_busstops = []
        request_processor.notify_about_other_busstops_if_required(
            location, other_busstops, self.sender_id)
        self.mock_call_send_api.assert_not_called()

    @patch.object(BusstopProcessor, 'process')
    def test_get_equivalent_busstop_match_empty_others(self, mock_busstop_processor_process):
        """non complex location is one that does not have an asterisk in front"""
        self.setup_call_api_for_success()
        pako = BusStopFactory(name='pako', area='surulere')
        mock_busstop_processor_process.return_value = {
            'match': pako, 'others': []}
        busstop = request_processor.get_equivalent_busstop(
            'pako', self.sender_id)
        self.assertEqual(busstop, pako)
        self.mock_call_send_api.assert_not_called()

    @patch.object(BusstopProcessor, 'process')
    def test_get_equivalent_busstop_match_two_others(self, mock_busstop_processor_process):
        """complex location is one that has an asterisk in front e.g. *ogunlana drive, surulere"""
        self.setup_call_api_for_success()
        pako = BusStopFactory(name='pako', area='surulere')
        ogunlana = BusStopFactory(name='ogunlana', area='surulere')
        lawanson = BusStopFactory(name='lawanson', area='surulere')

        mock_busstop_processor_process.return_value = {
            'match': pako, 'others': [ogunlana, lawanson]}

        busstop = request_processor.get_equivalent_busstop(
            '*ebun street, surulere', self.sender_id)
        self.assertEqual(busstop, pako)

        self.mock_call_send_api.assert_called_once()
        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        for busstop in [ogunlana.name, lawanson.name]:
            self.assertIn(busstop, call_send_api_arg)

    @patch('messager.request_processor.logger.warning')
    @patch.object(BusstopProcessor, 'process')
    def test_get_equivalent_busstop_no_match(self, mock_busstop_processor_process, mock_logger):
        self.setup_call_api_for_success()
        mock_busstop_processor_process.return_value = {
            'match': None, 'others': []}
        with self.assertRaises(BusStopNotFoundException):
            request_processor.get_equivalent_busstop('pako', self.sender_id)
            mock_logger.assert_called_with(dict(
                msg=ANY, location='pako',
                type='get_equivalent_busstop_failed', sender_id=self.sender_id
            ))
            self.mock_call_send_api.assert_not_called()

    @patch.object(RouteEngine, 'get_routes')
    def test_find_routes_when_routes_found(self, mock_route_engine_get_routes):
        self.setup_call_api_for_success()
        expected_routes = [['lawanson', 'ogunlana', 'ojuelegba']]
        mock_route_engine_get_routes.return_value = expected_routes
        lawanson = BusStopFactory(name='lawanson', area='surulere')
        ojuelegba = BusStopFactory(name='ojuelegba', area='surulere')
        routes = request_processor.find_routes(lawanson, ojuelegba)
        self.assertEqual(routes, expected_routes)

    @patch('messager.request_processor.logger.warning')
    @patch.object(RouteEngine, 'get_routes')
    def test_find_routes_when_no_routes_found(self, mock_route_engine_get_routes, mock_logger):
        self.setup_call_api_for_success()
        expected_routes = []
        mock_route_engine_get_routes.return_value = expected_routes
        lawanson = BusStopFactory(name='lawanson', area='surulere')
        ojuelegba = BusStopFactory(name='ojuelegba', area='surulere')
        with self.assertRaises(NoRouteFoundException):
            request_processor.find_routes(lawanson, ojuelegba)
            mock_logger.assert_called_once_with(dict(
                msg=ANY, source=lawanson, destination=ojuelegba,
                type='no_route_found'
            ))

    def test_format_routes_with_routes(self):
        routes = [
            ['lawanson', 'ogunlana', 'ojuelegba'],
            ['masha', 'shita', 'stadium', 'barracks', 'ojuelegba']
        ]
        result = request_processor.format_routes(routes)
        for idx, route in enumerate(result):
            for node in routes[idx]:
                self.assertIn(node, route)

    def test_format_routes_with_empty_routes(self):
        result = request_processor.format_routes([])
        self.assertEqual(result, [])

    def test_deconstruct_message_proper_format(self):
        result = request_processor.deconstruct_message(
            'ogunlana, surulere; cms, lagos island')
        self.assertEqual(len(result), 2)
        self.assertIn('ogunlana', result[0])
        self.assertIn('cms', result[1])

    def test_deconstruct_message_invalid_format_1(self):
        with self.assertRaises(FormatException):
            request_processor.deconstruct_message(
                'cms, lagos island, ogunlana, surulere')

    def test_deconstruct_message_invalid_format_2(self):
        with self.assertRaises(FormatException):
            request_processor.deconstruct_message(
                'ogunlana, surulere')

    def test_deconstruct_message_invalid_format_3(self):
        with self.assertRaises(FormatException):
            request_processor.deconstruct_message(
                'ogunlana, surulere;')

    @patch('messager.request_processor.fetch_users_first_name')
    def test_get_users_first_name_when_no_first_name(self, mock_fetch_users_first_name):
        request_processor.FIRST_NAME = ''
        mock_fetch_users_first_name.return_value = 'test_user'
        first_name = request_processor.get_users_first_name(self.sender_id)
        self.assertEqual(first_name, mock_fetch_users_first_name.return_value)
        mock_fetch_users_first_name.assert_called_once_with(self.sender_id)

    @patch('messager.request_processor.fetch_users_first_name')
    def test_get_users_first_name_global_has_first_name(self, mock_fetch_users_first_name):
        request_processor.FIRST_NAME = 'test_user'
        first_name = request_processor.get_users_first_name(self.sender_id)
        mock_fetch_users_first_name.assert_not_called()

    def test_is_greeting_text(self):
        some_greetings = ('Hello', 'HI', 'HOW are YOU', 'hiya',
                          'how far', 'Whats up?', "What's up")
        for greeting in some_greetings:
            self.assertTrue(request_processor.is_greeting_text(greeting))

    def test_is_greeting_with_non_greeting(self):
        non_greetings = ('Help', 'party', 'are you fine?', 'How is it?')
        for greeting in non_greetings:
            self.assertFalse(request_processor.is_greeting_text(greeting))

    @patch('messager.facebook_requests.requests.get')
    def test_get_greeting_returns_users_name_in_greeting(self, mock_requests_get):
        request_processor.FIRST_NAME = ''
        response = testing_utils.Response(200, 'test_user')
        mock_requests_get.return_value = response
        greeting = request_processor.get_greeting(self.sender_id)
        self.assertIn(response.first_name, greeting)

    @patch('messager.facebook_requests.requests.get')
    def test_get_greeting_returns_greeting_when_first_name_fetch_fails(self, mock_requests_get):
        request_processor.FIRST_NAME = ''
        response = testing_utils.Response(400)
        mock_requests_get.return_value = response
        greeting = request_processor.get_greeting(self.sender_id)
        self.assertNotEqual(greeting, '')
        self.assertIn('Hi', greeting)
