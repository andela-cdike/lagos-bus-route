"""Functions here prepare and send messages"""
from __future__ import unicode_literals

from messager.facebook_requests import call_send_api
from messager.renderers import render_text_message


def send_text_message(recipient_id, message):
    """Sends text message using facebook messenger's text message format

    recipient_id - - a string of the recipient's id
    message - - message to send to recipient
    """
    message = render_text_message(recipient_id, message)
    call_send_api(message)


def send_typing_action(recipient_id):
    """Sends typing action to user so he/she feels something is going on
    """
    message_data = {
        'recipient': {
            'id': recipient_id,
        },
        'sender_action': 'typing_on'
    }
    call_send_api(message_data)


def send_instructions(recipient_id):
    """Send usage instructions or command format"""
    template = (
        "Send your queries in any of these formats: \n"
        "1. If you are sure about the bus stop: \n"
        "<source bus stop>, <lga>; <destination bus stop>, <lga> \n"
        "e.g. oshodi, oshodi-isolo; cms, lagos island\n"
        "2. If you aren't sure about the bus stop or the lga "
        "(which would be most of the time \U0001f601) : \n"
        "-- *<source location>, <optional area>; *<destination location>, <optional area> \n"
        "-- e.g. *ketu; *sabo, yaba \n"
        "-- e.g. *mobolaji bank anthony; *eko hotel, victoria island \n"
        "-- <source bus stop> <lga>; *<destination location>, <optional area> \n"
        "-- e.g. cms, lagos island; *ogunlana drive, surulere \n"
    )
    send_text_message(recipient_id, template)


def send_routes(recipient_id, routes):
    """Send message for each route found

    : param recipient_id: string
    : param routes: a list of lists
    """
    for route in routes:
        send_text_message(recipient_id, route)
