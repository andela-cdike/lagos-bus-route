import logging

from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from busstops.exceptions import BusStopNotFoundException
from lagos_bus_route.celery import app
from messager.request_processor import (
    deconstruct_message, find_routes, get_equivalent_busstop, format_routes
)
from messager.message_senders import send_routes, send_text_message


@app.task
def handle_route_calculation_request(sender_id, request):
    """
    Takes the request from the user, interpretes it and sends a message
    to the user containing the route from the source to destination
    """
    source, destination = deconstruct_message(sender_id, request)
    try:
        source = get_equivalent_busstop(source, sender_id)
        destination = get_equivalent_busstop(destination, sender_id)
    except BusStopNotFoundException as exc:
        send_text_message(sender_id, exc.message)
    else:
        routes = find_routes(source, destination)
        send_routes(sender_id, format_routes(routes))
