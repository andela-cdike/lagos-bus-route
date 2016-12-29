from django.test import TestCase

from factories.factories import RouteFactory


class RouteModelTestSuite(TestCase):
    def test_model_string_representation(self):
        route_node = RouteFactory()
        exp_output = '{0}, type-{1}, route {2}'.format(
            route_node.busstop.name,
            route_node.busstop_type,
            route_node.route_id
        )
        self.assertEqual(str(route_node), exp_output)
