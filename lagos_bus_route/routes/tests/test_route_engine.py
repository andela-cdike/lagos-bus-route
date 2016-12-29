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

from route_fixtures import RouteFactoryDataSetup

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
