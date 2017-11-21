from mock import ANY, patch
from unittest import TestCase

from busstops.busstop_processor import BusstopProcessor
from busstops.exceptions import BusStopNotFoundException
from factories.factories import BusStopFactory
from routes.exceptions import NoRouteFoundException
from routes.route_engine import RouteEngine

from messager import tasks
from messager.exceptions import FormatException
from messager.tests import testing_utils


class HandleRouteCalculationRequest(TestCase):
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

    @patch.object(RouteEngine, 'get_routes')
    @patch.object(BusstopProcessor, 'process')
    def test_happy_path(self, mock_process, mock_get_routes):
        self.setup_call_api_for_success()
        pako = BusStopFactory(name='pako', area='surulere')
        mock_process.return_value = {'match': pako, 'others': []}

        routes = [['lawanson', 'pako', 'iyana-itire']]
        mock_get_routes.return_value = routes

        request = 'pako, surulere; iyana-itire, surulere'
        tasks.handle_route_calculation_request(self.sender_id, request)

        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.mock_call_send_api.assert_called_once()
        self.assertIn(self.sender_id, call_send_api_arg)
        for node in routes[0]:
            self.assertIn(node, call_send_api_arg)

    def test_format_exception_handled(self):
        self.setup_call_api_for_success()
        tasks.handle_route_calculation_request(
            self.sender_id, 'pako, surulere')
        self.assertEqual(self.mock_call_send_api.call_count, 2)

    @patch.object(BusstopProcessor, 'process', side_effect=BusStopNotFoundException('Failed!!'))
    def test_bus_stop_not_found_exception_handled(self, _):
        self.setup_call_api_for_success()
        tasks.handle_route_calculation_request(
            self.sender_id, 'fake busstop, surulere; pako, surulere')
        self.mock_call_send_api.assert_called_once()

        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.assertIn('Failed!!', call_send_api_arg)
        self.assertIn(self.sender_id, call_send_api_arg)

    @patch.object(BusstopProcessor, 'process')
    @patch.object(RouteEngine, 'get_routes', side_effect=NoRouteFoundException('Failed!!'))
    def test_bus_stop_not_found_exception_handled(self, _, mock_process):
        self.setup_call_api_for_success()
        pako = BusStopFactory(name='pako', area='surulere')
        mock_process.return_value = {'match': pako, 'others': []}

        tasks.handle_route_calculation_request(
            self.sender_id, 'pako, surulere; ogunlana, surulere')
        self.mock_call_send_api.assert_called_once()

        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.assertIn('Failed!!', call_send_api_arg)
        self.assertIn(self.sender_id, call_send_api_arg)

    @patch('messager.request_processor.notify_about_other_busstops_if_required',
           side_effect=KeyError('Failed!!'))
    @patch('messager.tasks.logger.error')
    @patch.object(RouteEngine, 'get_routes')
    @patch.object(BusstopProcessor, 'process')
    def test_random_exception_in_code(
            self, mock_process, mock_get_routes, mock_logger, _):
        self.setup_call_api_for_success()
        pako = BusStopFactory(name='pako', area='surulere', latitude='8.2323')
        mock_process.return_value = {'match': pako, 'others': []}

        routes = [['lawanson', 'pako', 'iyana-itire']]
        mock_get_routes.return_value = routes

        request = 'pako, surulere; iyana-itire, surulere'

        tasks.handle_route_calculation_request(self.sender_id, request)

        call_send_api_arg = unicode(self.mock_call_send_api.call_args[0][0])
        self.mock_call_send_api.assert_called_once()
        self.assertIn(self.sender_id, call_send_api_arg)

        mock_logger.assert_called_once_with(dict(
            msg=ANY, error=ANY, sender_id=self.sender_id,
            request=request,
            type='unhandled_handle_route_calculation_request_exception'
        ))
