import mock

from bus_fixtures import BusStopDataSetup
from busstops.busstop_processor import BusstopProcessor
from busstops.services.google_map_api_interface import GoogleMapApiInterface
from factories.factories import BusStopFactory


class BusstopProcessorTestSuite(BusStopDataSetup):
    def test_get_busstop_when_no_match(self):
        processor = BusstopProcessor('doesNotExist, nowhere')
        result = processor.process()
        exp_output = {
            'match': None,
            'others': []
        }
        self.assertEqual(exp_output, result)

    def test_get_busstop_with_busstop_match(self):
        processor = BusstopProcessor('ojuelegba, surulere')
        result = processor.process()
        exp_output = {
            'match': self.ojuelegba,
            'others': []
        }
        self.assertEqual(exp_output, result)

    def test_get_busstop_when_location_omits_area_single_match(self):
        processor = BusstopProcessor('ojuelegba')
        result = processor.process()
        exp_output = {
            'match': self.ojuelegba,
            'others': []
        }
        self.assertEqual(exp_output, result)

    def test_get_busstop_when_location_omits_area_multiple_matches(self):
        pako_one = BusStopFactory(name='pako', area='surulere')
        pako_two = BusStopFactory(name='pako', area='lagos mainland')
        processor = BusstopProcessor('pako')
        result = processor.process()
        exp_output = {
            'match': pako_one,
            'others': [pako_two]
        }
        self.assertEqual(exp_output, result)

    @mock.patch.object(
        GoogleMapApiInterface,
        'get_nearby_busstops',
        autospec=True,
        return_value=['lawanson', 'ogunlana']
    )
    def test_get_busstop_when_location_isnt_specific(self, mock_gmap_int_obj):
        processor = BusstopProcessor('*st mulumba catholic church, surulere')
        result = processor.process()
        exp_output = {
            'match': self.lawanson,
            'others': [self.ogunlana]
        }
        self.assertTrue(mock_gmap_int_obj.called)
        self.assertEqual(exp_output, result)