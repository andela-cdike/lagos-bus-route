import itertools
import logging
import Queue
from collections import namedtuple
from operator import itemgetter

from django.core.exceptions import MultipleObjectsReturned

from routes.models import Route


logger = logging.getLogger(__name__)


class RouteEngine(object):
    '''
    Args:
        start_busstop -- BusStop
        end_busstop -- BusStop
    '''
    BusstopNode = namedtuple(
        'BusstopNode', ['id', 'route_id', 'name', 'route', 'place_id', 'cost'])

    def __init__(self, start_busstop, end_busstop):
        self.start_busstop = start_busstop
        self.end_busstop = end_busstop
        self.route_ids_seen = set()
        self.route_id_queue = Queue.Queue()
        self.busstops_seen = set()
        self.busstops_queue = Queue.Queue()

    def get_routes(self):
        '''Entry point for the searching process
        Returns:
            found_routes -- a list of found routes
        '''
        start_busstop_node = self.BusstopNode(
            route_id=None,
            id=self.start_busstop.id,
            name=self.start_busstop.name,
            place_id=self.start_busstop.place_id,
            route=[self.start_busstop.name],
            cost=0
        )
        self.busstops_queue.put(start_busstop_node)
        found_routes = self._search_for_routes(start_busstop_node)
        found_routes.sort(key=itemgetter(1))
        min_cost = found_routes[0][1]
        return [route[0] for route in found_routes if route[1] < min_cost + 5]

    def _search_for_routes(self, start_busstop_node):
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
            self.busstops_seen.add(current_busstop_node.id)
            if self._is_destination(current_busstop_node):
                found_routes.append(
                    (list(current_busstop_node.route), current_busstop_node.cost))
            self._add_new_route_ids_to_queue(current_busstop_node)
            self._add_busstops_to_busstop_queue(current_busstop_node)
        return found_routes

    def _is_destination(self, busstop_node):
        '''Returns Boolean value indication if supplied busstop_node
        is the destination or not
        '''
        if busstop_node.place_id and self.end_busstop.place_id:
            return busstop_node.place_id == self.end_busstop.place_id
        return (busstop_node.name, busstop_node.area) == (self.end_busstop.name, self.end_busstop.area)

    def _add_new_route_ids_to_queue(self, busstop_node):
        '''
        Populate queue with all routes that the supplied busstops is a part of

        Args:
            busstop_node -- this method is to find all routes
                            this busstop belongs to
        '''
        instances_of_busstop = Route.objects.filter(
            busstop__id=busstop_node.id)
        for route in instances_of_busstop:
            if route.route_id not in self.route_ids_seen:
                self.route_id_queue.put(route.route_id)
        return self

    def _add_busstops_to_busstop_queue(self, busstop_node):
        '''
        Adds to bustops_queue all bus stops in all routes that
        the supplied busstop_node is a part of.
        '''
        while not self.route_id_queue.empty():
            route = self._get_route_nodes()
            ordered_route = self._order_route(route, busstop_node.id)
            ordered_route = [node for node in ordered_route
                             if node.busstop.id != busstop_node.id]
            for idx, node in enumerate(ordered_route, 1):
                if node.busstop.id not in self.busstops_seen:
                    accumulated_route = [
                        x for x in busstop_node.route + [
                            '{0} ({1} - {2})'.format(
                                node.busstop.name,
                                route.first().busstop.name,
                                route.last().busstop.name
                            )
                        ]]
                    queue_node = self.BusstopNode(
                        route_id=node.route_id,
                        id=node.busstop.id,
                        name=node.busstop.name,
                        place_id=node.busstop.place_id,
                        route=accumulated_route,
                        cost=busstop_node.cost + idx
                    )
                    self.busstops_queue.put(queue_node)
        return self

    def _get_route_nodes(self):
        '''Returns the nodes in a route as a queryset'''
        route_id = self.route_id_queue.get()
        self.route_ids_seen.add(route_id)
        return Route.objects.filter(route_id=route_id).order_by(
            'node_position')

    def _order_route(self, route, busstop_id):
        '''Order route based on supplied busstop argument
        The routes should be ordered based on the position of the supplied
        busstop in the route.

        If the busstop is a terminal and at the top of route, it should be
        returned without the node that has busstop_id.
        If the busstop is a terminal and at the bottom of route, it should be
        reversed and returned without the node that busstop_id
        If the busstop is not a terminal i.e. a transit station, it should  be
        split into two separate routes with the supplied busstop at the head
        of each.

        Args:
            route -- a queryset containing a bus route
            busstop_name -- id of the busstop in db
        Returns:
            route -- a list of the route
        '''
        try:
            node = route.get(busstop__id=busstop_id)
        except MultipleObjectsReturned as exc:
            logger.error(dict(
                msg='A route had duplicate busstop',
                route=route,
                busstop_id=busstop_id,
                type='_order_route'
            ))
            raise exc

        if node.id == route.first().id:
            return list(route)[1:]
        elif node.id == route.last().id:
            return list(route.order_by('-node_position'))[1:]
        return self._split_route_into_two(route, node)

    def _split_route_into_two(self, route, busstop_node):
        '''
        Splits the supplied route into two lists at the position of the
        supplied busstop_node effectively creating two routes with the
        supplied busstop at the head of each one. The busstop_node is
        removed before the route is returned

        Args:
            route -- a queryset containing a bus route
            busstop_node -- represents a record on the route database
        Returns:
            route -- a list representation of the route
        '''
        target_index = route.filter(
            node_position__lt=busstop_node.node_position).count()
        first_route = self._populate_new_route(route, 0, target_index)
        first_route.reverse()
        second_route = self._populate_new_route(
            route, target_index + 1, route.count())
        return first_route + second_route

    @staticmethod
    def _populate_new_route(route, start_index, stop_index):
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
