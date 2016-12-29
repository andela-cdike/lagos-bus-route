from collections import namedtuple
import Queue

from routes.models import Route


class RouteEngine(object):
    '''
    Args:

    '''
    BusstopNode = namedtuple('BusstopNode', ['route_id', 'name', 'route'])

    def __init__(self, start_busstop, end_busstop):
        self.start_busstop = start_busstop
        self.end_busstop = end_busstop
        self.route_ids_seen = {}
        self.route_id_queue = Queue.Queue()
        self.busstops_seen = {}
        self.busstops_queue = Queue.Queue()

    def get_routes(self):
        '''Entry point for the searching process
        Returns:
            found_routes -- a list of found routes
        '''
        start_busstop_node = self.BusstopNode(
            route_id=None,
            name=self.start_busstop,
            route=[self.start_busstop]
        )
        self.busstops_queue.put(start_busstop_node)
        found_routes = self.search_for_routes(start_busstop_node)
        return found_routes

    def search_for_routes(self, start_busstop_node):
        '''
        An implementation of the Breadth First Search Algorithm to find
        bus routes to a destination bus stop

        Args:
            start_busstop_node -- the origin busstop_node
        Returns:
            found_routes -- a list of found routes
        '''
        found_routes = []
        while not self.busstops_queue.empty():
            current_busstop_node = self.busstops_queue.get()
            self.busstops_seen[current_busstop_node.name] = True
            if self.is_destination(current_busstop_node):
                found_routes.append(current_busstop_node.route)
            self.add_new_route_ids_to_queue(current_busstop_node)
            self.add_busstops_to_busstop_queue(current_busstop_node)
        return found_routes

    def is_destination(self, busstop_node):
        '''Returns Boolean value indication if supplied busstop_node
        is the destination or not
        '''
        if busstop_node.name == self.end_busstop:
            return True
        return False

    def add_new_route_ids_to_queue(self, busstop_node):
        '''
        Populate queue with all routes that the supplied busstops is a part of

        Args:
            busstop_node -- this method is to find all routes
                            this busstop belongs to
        '''
        instances_of_busstop = Route.objects.filter(
            busstop__name=busstop_node.name)
        for route in instances_of_busstop:
            if route.route_id not in self.route_ids_seen:
                self.route_id_queue.put(route.route_id)
        return self

    def add_busstops_to_busstop_queue(self, busstop_node):
        '''
        Adds to bustops_queue all bus stops in all routes that
        the supplied busstop_node is a part of.
        '''
        while not self.route_id_queue.empty():
            route = self.get_route_nodes()
            ordered_route = self.order_route(route, busstop_node.name)
            for node in ordered_route:
                if node.busstop.name not in self.busstops_seen:
                    accumulated_route = [x for x in busstop_node.route]
                    accumulated_route.append(node.busstop.name)
                    queue_node = self.BusstopNode(
                        route_id=node.route_id,
                        name=node.busstop.name,
                        route=accumulated_route
                    )
                    self.busstops_queue.put(queue_node)
        return self

    def get_route_nodes(self):
        '''Returns the nodes in a route as a queryset'''
        route_id = self.route_id_queue.get()
        self.route_ids_seen[route_id] = True
        return Route.objects.filter(route_id=route_id).order_by('id')

    def order_route(self, route, busstop_name):
        '''Order route based on supplied busstop argument
        The routes should be ordered based on the position of the supplied
        busstop in the route.

        If the busstop is a terminal and at the top of route, it should be
        returned as is.
        If the busstop is a terminal and at the bottom of route, it should be
        reversed and returned
        If the busstop is not a terminal i.e. a transit station, it should  be
        split into two separate routes with the supplied busstop at the head
        of each.

        Args:
            route -- a queryset containing a bus route
            busstop_name -- string name of a busstop
        Returns:
            route -- a list of the route
        '''
        node = route.get(busstop__name=busstop_name)
        if node.id == route[0].id:
            return list(route)
        elif node.id == route[len(route) - 1].id:
            return list(route.order_by('-id'))
        return self.split_route_into_two(route, node)

    def split_route_into_two(self, route, busstop_node):
        '''
        Splits the supplied route into two lists at the position of the
        supplied busstop_node effectively creating two routes with the
        supplied busstop at the head of each one

        Args:
            route -- a queryset containing a bus route
            busstop_node -- represents a record on the route database
        Returns:
            route -- a list representation of the route
        '''
        target_index = route.filter(busstop__id__lt=busstop_node.id).count()
        first_route = self.populate_new_route(route, 0, target_index)
        first_route.append(busstop_node)
        first_route.reverse()
        second_route = self.populate_new_route(
            route, target_index, route.count())
        return first_route + second_route

    def populate_new_route(self, route, start_index, stop_index):
        '''
        Returns a subset of the route provided as a new route

        Args:
            route -- a queryset containing a bus route
            index -- a positional index indicating terminal point of the loop
        Returns:
            a list representation of the route
        '''
        new_route = []
        index = start_index
        while index < stop_index:
            new_route.append(route[index])
            index += 1
        return new_route
