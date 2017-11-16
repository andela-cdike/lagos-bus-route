"""Exceptions for the routes app"""


class NoRouteFoundException(Exception):
    """
    Raise this exception when no route is found between a
    source and destination bus stop
    """
