"""Celery tasks for the messager app"""
import logging

from busstops.exceptions import BusStopNotFoundException
from lagos_bus_route.celery import app
from messager.exceptions import FormatException
from messager.messengers import (
    send_instructions, send_routes, send_text_message
)
from messager.request_processor import (
    deconstruct_message, find_routes, get_equivalent_busstop, format_routes
)


logger = logging.getLogger(__name__)


@app.task
def handle_route_calculation_request(sender_id, request):
    """
    Takes the request from the user, interpretes it and sends a message
    to the user containing the route from the source to destination
    """
    try:
        try:
            source, destination = deconstruct_message(request)
        except FormatException as exc:
            send_text_message(sender_id, exc.message)
            send_instructions(sender_id)
        else:
            try:
                source = get_equivalent_busstop(source, sender_id)
                destination = get_equivalent_busstop(destination, sender_id)
            except BusStopNotFoundException as exc:
                send_text_message(sender_id, exc.message)
            else:
                routes = find_routes(source, destination)
                send_routes(sender_id, format_routes(routes))
    except Exception as exc:
        logger.error(dict(
            msg='An unhandled exception occurred',
            error=exc,
            type='unhandled_handle_route_calculation_request_exception'))
        send_text_message(sender_id,
                          'Ooops, something went wrong. Please try again')
