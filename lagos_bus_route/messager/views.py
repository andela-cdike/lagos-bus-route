import json
import logging
import os
import time

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import requests

from busstops.busstop_processor import BusstopProcessor

from routes.route_engine import RouteEngine


logger = logging.getLogger(__name__)


class FormatException(Exception):
    """Raise this exception for wrongly formatted messages"""


@method_decorator(csrf_exempt, 'dispatch')
class Webhook(View):
    def get(self, request, *args, **kwargs):
        """when the endpoint is registered as a webhook, it must echo back
        the 'hub.challenge' value it receives in the query arguments
        """
        is_subscribe = request.GET.get('hub.mode') == 'subscribe'
        challenge = request.GET.get('hub.challenge')
        is_valid_verify_token = (
            request.GET.get('hub.verify_token') == os.getenv('VERIFY_TOKEN')
        )
        if is_subscribe and challenge:
            if not is_valid_verify_token:
                return HttpResponseForbidden('Verification token mismatch')

            return HttpResponse(challenge)
        return HttpResponse("Don't know how to deal with this yet")

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        # make sure it is a page subscription
        if data['object'] == 'page':
            # iterate over each entry - there may be multiple if batched
            for entry in data['entry']:
                page_id = entry['id']
                time_of_event = entry['time']

                # iterate over each messaging event
                for event in entry['messaging']:
                    if event['message']:
                        try:
                            handle_message(event)
                        except FormatException:
                            pass
                        except Exception as exc:
                            print exc
                            logger.error(dict(msg='An unhandled exception in handle_message',
                                              event=event,
                                              error=exc,
                                              type='unhandled_handle_message_exception'))
                            send_text_message(
                                event['sender']['id'],
                                'Ooops, something went wrong. Please try again')
                    else:
                        logger.warn(dict(msg='Webhook received unknown event',
                                         event=event,
                                         type='webhook_unknown_event'))

        # Assume all went well.
        #
        # You must send back a 200, within 20 seconds, to let us know
        # you've successfully received the callback. Otherwise, the request
        # will time out and we will keep trying to resend.
        # This means I have to use celery for the calculation
        return HttpResponse()


def get_equivalent_busstop(location):
    """
    Returns a busstop in the database for the location supplied
    """
    bp = BusstopProcessor(location)
    busstops = bp.process()
    return busstops['match']


def find_routes(source, destination):
    """
    Calls the route engine to return a route between source and destination

    : param source: string
    : param destination: string
    """
    rtengine = RouteEngine(source, destination)
    routes = rtengine.get_routes()
    return routes


def format_routes(routes):
    """Return message in a user - friendly format

    routes - - a list of list
    """
    results = []
    for route in routes:
        results.append(' -> '.join(route))
    return results


def send_routes(recipient_id, routes):
    """Send message for each route found

    : param recipient_id: string
    : param routes: a list of lists
    """
    for route in routes:
        send_text_message(recipient_id, route)


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


def render_text_message(recipient_id, message):
    """
    Constructs and returns the message in messenger format

    recipient_id - - the receivers address
    message - - message text
    """
    return {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message
        }
    }


def send_text_message(recipient_id, message):
    """Sends text message using facebook messenger's text message format

    recipient_id - - a string of the recipient's id
    message - - message to send to recipient
    """
    message = render_text_message(recipient_id, message)
    call_send_api(message)


def send_typing_action(recipient_id):
    """Sends typing action to user so he / she feels something is going on
    """
    message_data = {
        'recipient': {
            'id': recipient_id,
        },
        'sender_action': 'typing_on'
    }
    call_send_api(message_data)


def call_send_api(message_data):
    """Makes HTTP requests to Facebook to respond to users: )

    message_data - - a dictionary of the message in messenger's text format
                    including the recipient's ID
    """
    url = 'https://graph.facebook.com/v2.6/me/messages'
    params = {
        'access_token': os.getenv('PAGE_ACCESS_TOKEN')
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, params=params,
                             headers=headers, json=message_data)

    if response.status_code == 200:
        logger.info({
            'msg': 'Response successfully sent',
            'message_data': message_data,
            'type': 'call_send_api_successful'
        })
    else:
        logger.warning({
            'msg': 'Sending response failed!!!',
            'message_data': message_data,
            'response': response.json(),
            'type': 'call_send_api_unsuccessful'
        })


def is_valid(message_text):
    """There are two main formats for messages to this service

    The first format can be used when you are almost sure
    of a busstop:
    - source_busstop, lga; destination_busstop, lga

    The second format is used when you are unsure. You simply
    add an * infront of a place, landmark, or area and the app does
    the rest
    # TODO: Verify the use of this
    - *source, lga; *destination, lga
    """
    return True


def verify_have_route_for_busstops(source, destination):
    """
    Confirms that there are routes for the source and destination
    source - - string
    destination - - string
    """
    pass


# a celery task, I think
def find_route(source, destination):
    """
    Calls route engine to find the route between source and destination
    source - - string
    destination - - string
    """
    pass


def handle_message(event):
    """
    Interpretes message and sends routes to user if found
    Sends error messages if there are issues
    """
    sender_id = event['sender']['id']
    recipient_id = event['recipient']['id']
    time_of_message = event['timestamp']
    message = event.get('message')

    logger.info({
        'msg': 'Received message',
        'sender_id': sender_id,
        'recipient_id': recipient_id,
        'message': message,
        'type': 'webhook_received_message'
    })

    message_text = message.get('text')
    message_attachments = message.get('attachments')

    if message_text and is_valid(message_text):
        send_typing_action(sender_id)
        # run as task: celery and redis
        source, destination = deconstruct_message(sender_id, message_text)
        source = get_equivalent_busstop(source)
        destination = get_equivalent_busstop(destination)
        routes = find_routes(source, destination)
        send_routes(sender_id, format_routes(routes))
    elif message_attachments:
        send_text_message(sender_id, "Sorry, we don't support attachments.")
