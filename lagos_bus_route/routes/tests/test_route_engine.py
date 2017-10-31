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
from __future__ import unicode_literals

from mock import MagicMock
import random

from busstops.models import BusStop

from route_fixtures import RouteFactoryDataSetup
from routes.models import Route
from routes.route_engine import RouteEngine


def remove_route_info(node):
    """I don't know how long I am going to be leaving the name of
    route in the route returned from route_engine.
    IN the meantime, this function would remove the metadata
    When it receives: ojuelegba (lawanson - yaba), it removes the
    space and parenthesis after ojuelegba. Returns just ojuelegba
    :arg node: name of node
    :returns: cleaned node
    """
    target_index = node.find(' (')
    return node[:target_index if target_index != -1 else len(node) + 1]


class RouteEngineTestSuite(RouteFactoryDataSetup):
    def test_get_route_starts_terminal_ends_node_level_one(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='municipal')
        routes = RouteEngine(start, end).get_routes()
        result = [remove_route_info(node)
                  for route in routes for node in route]
        exp_output = ['lawanson', 'municipal']
        self.assertEqual(exp_output, result)

    def test_get_route_starts_terminal_ends_terminal_level_one(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        routes = RouteEngine(start, end).get_routes()
        result = [remove_route_info(node)
                  for route in routes for node in route]
        exp_output = ['lawanson', 'ojuelegba']
        self.assertEqual(exp_output, result)

    def test_get_route_starts_node_ends_node_level_one(self):
        start = BusStop.objects.get(name='ogunlana')
        end = BusStop.objects.get(name='ishaga')
        routes = RouteEngine(start, end).get_routes()
        result = [remove_route_info(node)
                  for route in routes for node in route]
        exp_output = ['ogunlana', 'ishaga']
        self.assertEqual(exp_output, result)

    def test_get_route_starts_terminal_ends_node_level_two(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='idi-oro')
        routes = RouteEngine(start, end).get_routes()
        result = [remove_route_info(node)
                  for route in routes for node in route]
        exp_output = ['lawanson', 'ojuelegba', 'idi-oro']
        self.assertEqual(exp_output, result)

    def test_get_route_starts_node_ends_node_level_two(self):
        start = BusStop.objects.get(name='ogunlana')
        end = BusStop.objects.get(name='idi-oro')
        routes = RouteEngine(start, end).get_routes()
        result = [remove_route_info(node)
                  for route in routes for node in route]
        exp_output = ['ogunlana', 'ojuelegba', 'idi-oro']
        self.assertEqual(exp_output, result)

    def test_get_route_starts_node_ends_terminal_level_two(self):
        start = BusStop.objects.get(name='ogunlana')
        end = BusStop.objects.get(name='mushin')
        routes = RouteEngine(start, end).get_routes()
        result = [remove_route_info(node)
                  for route in routes for node in route]
        exp_output = ['ogunlana', 'ojuelegba', 'mushin']
        self.assertEqual(exp_output, result)

    def test_get_route_starts_terminal_ends_termina_level_three(self):
        start = BusStop.objects.get(name='mushin')
        end = BusStop.objects.get(name='cele')
        routes = RouteEngine(start, end).get_routes()
        result = [remove_route_info(node)
                  for route in routes for node in route]
        exp_output = ['mushin', 'ojuelegba', 'lawanson', 'cele']
        self.assertEqual(exp_output, result)

    def test_get_route_starts_terminal_ends_node_level_three(self):
        start = BusStop.objects.get(name='mushin')
        end = BusStop.objects.get(name='itire road junction')
        routes = RouteEngine(start, end).get_routes()
        result = [remove_route_info(node)
                  for route in routes for node in route]
        exp_output = ['mushin', 'ojuelegba', 'lawanson', 'itire road junction']
        self.assertEqual(exp_output, result)

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
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        route = Route.objects.filter(route_id=1).order_by('node_position')
        target_busstop_index = 2
        new_route = RouteEngine(start, end)._split_route_into_two(
            route, route[target_busstop_index])
        # result should have the the supplied busstop node at the head of two
        # subroutes generated from the supplied route
        # these subroutes are simply the route from the busstop_node to the
        # terminal busstops of the route (with the current busstop_node removed)
        exp_output = [route[1], route[0], route[3], route[4]]
        self.assertEqual(exp_output, new_route)

    def test_order_route_when_supplied_busstop_is_at_start_node_position(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        route = Route.objects.filter(route_id=1).order_by('node_position')
        result = rtengine._order_route(route, end.id)
        exp_output = [node for node in route if node.busstop != end]
        self.assertEqual(exp_output, result)

    def test_order_route_when_supplied_busstop_is_at_stop_node_position(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        route = Route.objects.filter(route_id=1).order_by('node_position')
        result = rtengine._order_route(route, start.id)
        exp_output = [node for node in route if node.busstop != start]
        exp_output.reverse()
        self.assertEqual(exp_output, result)

    def test_order_route_when_supplied_busstop_is_not_a_terminal_busstop(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        route = Route.objects.filter(route_id=1).order_by('node_position')
        rtengine._populate_new_route = MagicMock()
        municipal = BusStop.objects.get(name='municipal')
        rtengine._order_route(route, municipal.id)
        rtengine._populate_new_route.called_once()

    def test_get_route_nodes(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        route_id = 1
        rtengine.route_id_queue.put(route_id)
        result = rtengine._get_route_nodes()
        exp_output = Route.objects.filter(route_id=route_id).order_by(
            'node_position')
        for index in xrange(len(result)):
            self.assertEqual(exp_output[index], result[index])

    def test_add_busstops_to_busstop_queue_busstop_node_in_one_route_non_terminal(
            self):
        start = BusStop.objects.get(name='municipal')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        route_id = 1
        rtengine.route_id_queue.put(route_id)
        busstop_node = rtengine.BusstopNode(
            id=start.id,
            route_id=0,
            name=start.name,
            place_id=start.place_id,
            route=[start.name],
            cost=0
        )
        rtengine._add_busstops_to_busstop_queue(busstop_node)
        num_of_busstops_in_route = Route.objects.filter(
            route_id=route_id).count()
        self.assertEqual(
            rtengine.busstops_queue.qsize(),
            # target busstop is not counted since it has already
            # been considered
            num_of_busstops_in_route - 1
        )

    def test_add_busstops_to_busstop_queue_busstop_node_two_routes_terminal(
            self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        route_id = 1
        rtengine.route_id_queue.put(route_id)
        busstop_node = rtengine.BusstopNode(
            id=end.id,
            route_id=0,
            name=end.name,
            place_id=end.place_id,
            route=[end.name],
            cost=0
        )
        rtengine._add_busstops_to_busstop_queue(busstop_node)
        num_of_busstops_in_route = Route.objects.filter(
            route_id=route_id).count()

        self.assertEqual(
            rtengine.busstops_queue.qsize(),
            num_of_busstops_in_route - 1
        )

    def test_add_new_route_ids_to_queue(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        busstop_node = rtengine.BusstopNode(
            id=end.id,
            route_id=0,
            name=end.name,
            place_id=end.place_id,
            route=[end.name],
            cost=0
        )
        rtengine._add_new_route_ids_to_queue(busstop_node)
        num_routes_connected_to_ojuelegba = Route.objects.filter(
            busstop__name='ojuelegba').count()
        self.assertEqual(
            rtengine.route_id_queue.qsize(), num_routes_connected_to_ojuelegba)

    def test_is_destination_with_true_destination(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        busstop_node = rtengine.BusstopNode(
            id=end.id,
            route_id=0,
            name=end.name,
            place_id=end.place_id,
            route=[end.name],
            cost=0
        )
        self.assertEqual(rtengine._is_destination(busstop_node), True)

    def test_is_destination_with_false_destination(self):
        start = BusStop.objects.get(name='lawanson')
        end = BusStop.objects.get(name='ojuelegba')
        rtengine = RouteEngine(start, end)
        busstop_node = rtengine.BusstopNode(
            id=self.municipal.id,
            route_id=0,
            name=self.municipal.name,
            place_id='place_id_for_municipal',
            route=[self.municipal.name],
            cost=0
        )
        self.assertEqual(rtengine._is_destination(busstop_node), False)

    def test_search_for_routes(self):
        start = BusStop.objects.get(name='municipal')
        end = BusStop.objects.get(name='ishaga')
        rtengine = RouteEngine(start, end)
        busstop_node = rtengine.BusstopNode(
            id=start.id,
            route_id=0,
            name=start.name,
            place_id=start.place_id,
            route=[start.name],
            cost=0
        )
        rtengine.busstops_queue.put(busstop_node)
        result = rtengine._search_for_routes(busstop_node)
        result = [name.split()[0] for node in result for name in node[0]]
        exp_output = ['municipal', 'ishaga']
        self.assertEqual(exp_output, result)
