import unittest

from django.test import TestCase

from busstops.services.google_map_api_interface import GoogleMapApiInterface


@unittest.skip('Skip tests that make API calls')
class GoogleMapApiInterfaceTestSuite(TestCase):
    def setUp(self):
        self.gmapi = GoogleMapApiInterface()
        self.address = 'ogunlana drive surulere'

    def test_get_coordinates(self):
        coordinate = self.gmapi.get_coordinates(self.address)
        self.assertTrue('lat' in coordinate)
        self.assertTrue('lng' in coordinate)

    def test_get_nearby_busstops(self):
        result = self.gmapi.get_nearby_busstops(self.address)
        self.assertEqual(type(result), list)
        self.assertGreater(result, [])

    def test_get_nearby_busstops_with_no_result(self):
        address = 'hopefully_this_address_never_matches_a_real_address'
        result = self.gmapi.get_nearby_busstops(address)
        self.assertEqual(result, [])
