from __future__ import unicode_literals

import functools
import jellyfish
import logging

from busstops.busstop_processor import BusstopProcessor
from busstops.exceptions import BusStopNotFoundException
from routes.route_engine import RouteEngine

from messager.exceptions import FormatException
from messager.message_senders import (
    send_instructions, send_text_message, send_typing_action
)
from messager.facebook_requests import fetch_users_first_name


logger = logging.getLogger(__name__)
first_name = ''


def notify_about_other_busstops_if_required(
        location, other_busstops, sender_id):
    """
    Notifies users of alternative busstops if any is returned from
    google map api
    :param location: a string, a location (src or destination) supplied by
                     the user
    :param other_busstops: a list of BusStops
    :param sender_id: a string
    """
    if other_busstops:
        busstops_list = zip(range(1, len(other_busstops) + 1), other_busstops)
        busstops_list = "\n".join([
            '{0:2d}. {1}'.format(idx, busstop) for idx, busstop in busstops_list
        ])
        message = "Here are other busstops we found around {0}:\n {1}".format(
            location, busstops_list)
        send_text_message(sender_id, message)


def get_equivalent_busstop(location, sender_id):
    """
    Returns a busstop in the database for the location supplied
    :param location: a string
    :param sender_id: a string
    """
    busstops = BusstopProcessor(location).process()
    if not busstops.get('match'):
        msg = 'No busstop was found for "{}"'.format(location.strip())
        logger.warning(dict(
            msg=msg,
            location=location,
            type='get_equivalent_busstop'
        ))
        raise BusStopNotFoundException(msg)
    notify_about_other_busstops_if_required(
        location, busstops['others'], sender_id)
    return busstops['match']


def find_routes(source, destination):
    """
    Calls the route engine to return a route between source and destination

    : param source: string
    : param destination: string
    """
    return RouteEngine(source, destination).get_routes()


def format_routes(routes):
    """Return message in a user - friendly format

    routes - - a list of list
    """
    results = []
    for route in routes:
        results.append(' -> '.join(route))
    return results


def deconstruct_message(recipient_id, message):
    """Splits the message to its component part:
    source and destination

    : param recipient_id:
    : param message: -- (string) message received from user
    : returns: a tuple of the source and destination parts of the address
    """
    components = message.split(';')
    if len(components) != 2:
        error_msg = ('Your message -> {message}\n is in an invalid format.')
        send_text_message(recipient_id, error_msg.format(message=message))
        raise FormatException
    return components


def get_users_first_name(sender_id):
    global first_name
    if not first_name:
        first_name = fetch_users_first_name(sender_id)
    return first_name


def is_greeting_text(message):
    """Returns True if message is a greeting, else False"""
    greeting_text = ('hello', 'hi', 'how are you',
                     'whats up', 'how far', 'hey')
    jd_with_message = functools.partial(
        jellyfish.jaro_distance, message)
    return any(jd_with_message(text) > .8 for text in greeting_text)


def get_greeting(sender_id):
    """Returns a random greeting out of a collection of greetings"""
    first_name = get_users_first_name(sender_id)
    return 'Hi {0}\nType in your query to get started.'.format(first_name)
