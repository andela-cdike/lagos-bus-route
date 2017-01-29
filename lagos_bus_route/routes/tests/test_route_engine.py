'''
Tests module for the RouteEngine class

There are certain method naming conventions that would be observed
for this file:
    starts -- refers to the start bus stop
    ends -- refers to end bus stop
    level -- refers to how many routes are involved
            e.g.1   - one route
                2   - two routes. e.t.c.
'''
from mock import MagicMock
import random

from route_fixtures import RouteFactoryDataSetup
from routes.models import Route
from routes.route_engine import RouteEngine


class RouteEngineTestSuite(RouteFactoryDataSetup):
    # def setUp(self, *args, **kwargs):
    #     super(RouteEngineTestSuite, self).setUp(*args, **kwargs)
    #     self.rtengine = RouteEngine('lawanson', 'yaba')

    def test_get_route_starts_terminal_ends_node_level_one(self):
        rtengine = RouteEngine('lawanson', 'municipal')
        routes = rtengine.get_routes()
        exp_output = [['lawanson', 'municipal']]
        self.assertEqual(exp_output, routes)

    def test_get_route_starts_terminal_ends_terminal_level_one(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        routes = rtengine.get_routes()
        exp_output = [['lawanson', 'ojuelegba']]
        self.assertEqual(exp_output, routes)

    def test_get_route_starts_node_ends_node_level_one(self):
        rtengine = RouteEngine('ogunlana', 'ishaga')
        routes = rtengine.get_routes()
        exp_output = [['ogunlana', 'ishaga']]
        self.assertEqual(exp_output, routes)

    def test_get_route_starts_terminal_ends_node_level_two(self):
        rtengine = RouteEngine('lawanson', 'idi oro')
        routes = rtengine.get_routes()
        exp_output = [['lawanson', 'ojuelegba', 'idi oro']]
        self.assertEqual(exp_output, routes)

    def test_get_route_starts_node_ends_node_level_two(self):
        rtengine = RouteEngine('ogunlana', 'idi oro')
        routes = rtengine.get_routes()
        exp_output = [['ogunlana', 'ojuelegba', 'idi oro']]
        self.assertEqual(exp_output, routes)

    def test_get_route_starts_node_ends_terminal_level_two(self):
        rtengine = RouteEngine('ogunlana', 'mushin')
        routes = rtengine.get_routes()
        exp_output = [['ogunlana', 'ojuelegba', 'mushin']]
        self.assertEqual(exp_output, routes)

    def test_get_route_starts_terminal_ends_termina_level_three(self):
        rtengine = RouteEngine('mushin', 'cele')
        routes = rtengine.get_routes()
        exp_output = [['mushin', 'ojuelegba', 'lawanson', 'cele']]
        self.assertEqual(exp_output, routes)

    def test_get_route_starts_terminal_ends_node_level_three(self):
        rtengine = RouteEngine('mushin', 'itire road junction')
        routes = rtengine.get_routes()
        exp_output = [
            ['mushin', 'ojuelegba', 'lawanson', 'itire road junction']
        ]
        self.assertEqual(exp_output, routes)

    def test_populate_new_route_start_0_end_random_inner(self):
        route = Route.objects.filter(route_id=1).order_by('node_position')
        start_index = 0
        stop_index = random.randint(start_index, route.count())
        populated_route = RouteEngine._populate_new_route(
            route, start_index, stop_index)
        exp_output = [
            r for index, r in enumerate(route) if index < stop_index
        ]
        self.assertEqual(exp_output, populated_route)

    def test_populate_new_route_start_random_inner_end_last(self):
        route = Route.objects.filter(route_id=1).order_by('node_position')
        stop_index = route.count()
        start_index = random.randint(0, stop_index - 1)
        populated_route = RouteEngine._populate_new_route(
            route, start_index, stop_index)
        exp_output = [r for r in route[start_index:]]
        self.assertEqual(exp_output, populated_route)

    def test_split_route_into_two(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        route = Route.objects.filter(route_id=1).order_by('node_position')
        target_busstop_index = 2
        new_route = rtengine._split_route_into_two(
            route, route[target_busstop_index])
        # result should have the the supplied busstop node at the head of two
        # subroutes generated from the supplied route
        # these subroutes are simply the route from the busstop_node to the
        # terminal busstops of the route
        exp_output = [
            route[2], route[1], route[0], route[2], route[3], route[4]
        ]
        self.assertEqual(exp_output, new_route)

    def test_order_route_when_supplied_busstop_is_at_start_node_position(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        route = Route.objects.filter(route_id=1).order_by('node_position')
        result = rtengine._order_route(route, 'ojuelegba')
        exp_output = list(route)
        self.assertEqual(exp_output, result)

    def test_order_route_when_supplied_busstop_is_at_stop_node_position(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        route = Route.objects.filter(route_id=1).order_by('node_position')
        result = rtengine._order_route(route, 'lawanson')
        exp_output = list(route)
        exp_output.reverse()
        self.assertEqual(exp_output, result)

    def test_order_route_when_supplied_busstop_is_not_a_terminal_busstop(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        route = Route.objects.filter(route_id=1).order_by('node_position')
        rtengine._populate_new_route = MagicMock()
        rtengine._order_route(route, 'municipal')
        rtengine._populate_new_route.called_once()

    def test_get_route_nodes(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        route_id = 1
        rtengine.route_id_queue.put(route_id)
        result = rtengine._get_route_nodes()
        exp_output = Route.objects.filter(route_id=route_id).order_by(
            'node_position')
        for index in xrange(len(result)):
            self.assertEqual(exp_output[index], result[index])

    def test_add_busstops_to_busstop_queue_busstop_node_in_one_route_non_term(
            self):
        rtengine = RouteEngine('municipal', 'ojuelegba')
        route_id = 1
        rtengine.route_id_queue.put(route_id)
        busstop_node = rtengine.BusstopNode(
            route_id=0,
            name='municipal',
            route=['municipal']
        )
        rtengine._add_busstops_to_busstop_queue(busstop_node)
        num_of_busstops_in_route = Route.objects.filter(
            route_id=route_id).count()
        self.assertEqual(
            rtengine.busstops_queue.qsize(),
            num_of_busstops_in_route + 1   # target busstop counts twice
                                           # because its not terminal
        )

    def test_add_busstops_to_busstop_queue_busstop_node_two_routes_terminal(
            self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        route_id = 1
        rtengine.route_id_queue.put(route_id)
        busstop_node = rtengine.BusstopNode(
            route_id=0,
            name='ojuelegba',
            route=['ojuelegba']
        )
        rtengine._add_busstops_to_busstop_queue(busstop_node)
        num_of_busstops_in_route = Route.objects.filter(
            route_id=route_id).count()

        self.assertEqual(
            rtengine.busstops_queue.qsize(),
            num_of_busstops_in_route
        )

    def test_add_new_route_ids_to_queue(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        busstop_node = rtengine.BusstopNode(
            route_id=0,
            name='ojuelegba',
            route=['ojuelegba']
        )
        rtengine._add_new_route_ids_to_queue(busstop_node)
        num_routes_connected_to_ojuelegba = Route.objects.filter(
            busstop__name='ojuelegba').count()
        self.assertEqual(
            rtengine.route_id_queue.qsize(), num_routes_connected_to_ojuelegba)

    def test_is_destination_with_true_destination(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        busstop_node = rtengine.BusstopNode(
            route_id=0,
            name='ojuelegba',
            route=['ojuelegba']
        )
        self.assertEqual(rtengine._is_destination(busstop_node), True)

    def test_is_destination_with_false_destination(self):
        rtengine = RouteEngine('lawanson', 'ojuelegba')
        busstop_node = rtengine.BusstopNode(
            route_id=0,
            name='municipal',
            route=['municipal']
        )
        self.assertEqual(rtengine._is_destination(busstop_node), False)

    def test_search_for_routes(self):
        rtengine = RouteEngine('municipal', 'ishaga')
        busstop_node = rtengine.BusstopNode(
            route_id=0,
            name='municipal',
            route=['municipal']
        )
        rtengine.busstops_queue.put(busstop_node)
        result = rtengine._search_for_routes(busstop_node)
        exp_output = [['municipal', 'ishaga']]
        self.assertEqual(exp_output, result)
