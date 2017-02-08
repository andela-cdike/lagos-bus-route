import unittest

from busstops.scripts import get_busstop_info_from_gapi


class MergeDictsTestCase(unittest.TestCase):
    def test_merge_dicts(self):
        a_dict = {'one': 1}
        b_dict = {'two': 2}
        c_dict = {'three': 3}
        exp_output = {'one': 1, 'two': 2, 'three': 3}
        result = get_busstop_info_from_gapi.merge_dicts(a_dict, b_dict, c_dict)
        self.assertEqual(exp_output, result)

    def test_merge_dicts_gives_precedence_to_later_dicts(self):
        a_dict = {'one': 1, 'two': 2}
        b_dict = {'two': 'two', 'three': 3}
        exp_output = {'one': 1, 'two': 'two', 'three': 3}
        result = get_busstop_info_from_gapi.merge_dicts(a_dict, b_dict)
        self.assertEqual(exp_output, result)


class GetApiKeyTestCase(unittest.TestCase):
    def test_get_api_key_returns_string(self):
        result = next(get_busstop_info_from_gapi.get_api_key())
        self.assertEqual(type(result), str)

    def test_get_api_key_returns_random_values(self):
        api_keys_generated = [next(get_busstop_info_from_gapi.get_api_key())]

        for i in xrange(3):
            api_key = get_busstop_info_from_gapi.get_api_key()
            self.assertTrue(api_key not in api_keys_generated)
            api_keys_generated.append(api_key)


class GetPlaceInfoFromGapiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api_key = 'AIzaSyCt7JdcEzFU14DcDEEY6edTZXoz0qbA8Ws'
        busstop_info = {
            'name': 'alaba',
            'area': 'surulere'
        }
        cls._result = get_busstop_info_from_gapi.get_place_info_from_gapi(
            api_key, busstop_info
        )

    def test_get_place_info_from_gapi_returns_dict(self):
        self.assertEqual(type(GetPlaceInfoFromGapiTestCase._result), dict)

    def test_get_place_info_from_gapi_has_right_keys(self):
        keys = GetPlaceInfoFromGapiTestCase._result.keys()
        exp_output = ('latitude', 'longitude', 'place_id')
        self.assertTrue(set(exp_output) <= set(keys))

    def test_get_place_info_from_gapi_has_values(self):
        values = GetPlaceInfoFromGapiTestCase._result.values()
        for val in values:
            self.assertIsNotNone(val)