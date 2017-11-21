from __future__ import unicode_literals

import ast
import json
import logging
import os

from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from messager.decorators import log_received_event
from messager.messengers import (
    send_instructions, send_text_message, send_typing_action
)
from messager.request_processor import get_greeting, is_greeting_text
from messager.tasks import handle_route_calculation_request


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, 'dispatch')
class Webhook(View):
    """Entry point to the messager app"""

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
        """This endpoint handles message received from messenger users"""
        data = json.loads(request.body)

        # make sure it is a page subscription
        if data['object'] == 'page':
            # iterate over each entry - there may be multiple if batched
            for entry in data['entry']:
                page_id = entry['id']
                time_of_event = entry['time']

                # iterate over each messaging event
                for event in entry['messaging']:
                    if event.get('message'):
                        try:
                            handle_message(event)
                        except Exception as exc:
                            logger.error(dict(
                                msg='An unhandled exception occured in handle_message',
                                event=event,
                                error=exc,
                                type='unhandled_handle_message_exception'))
                            send_text_message(
                                event['sender']['id'],
                                'Ooops, something went wrong. Please try again')
                    elif event.get('postback'):
                        handle_postback(event)
                    else:
                        logger.warning(dict(msg='Webhook received unknown event',
                                            event=event,
                                            type='webhook_unknown_event'))

        # Assume all went well.
        #
        # You must send back a 200, within 20 seconds, to let us know
        # you've successfully received the callback. Otherwise, the request
        # will time out and we will keep trying to resend.
        # This means I have to use celery for the calculation
        return HttpResponse()


@log_received_event
def handle_message(event):
    """
    Interpretes message and sends routes to user if found
    Sends error messages if there are issues
    """
    sender_id = event['sender']['id']
    message = event['message']

    message_text = message.get('text')
    message_attachments = message.get('attachments')
    send_typing_action(sender_id)

    if is_greeting_text(message_text) or 'help' in message_text.lower():
        send_text_message(sender_id, get_greeting(sender_id))
        send_instructions(sender_id)
    elif message_text:
        handle_route_calculation_request.delay(sender_id, message_text)
    elif message_attachments:
        send_text_message(sender_id, "Sorry, we don't support attachments.")


@log_received_event
def handle_postback(event):
    """Handles postback messages"""
    sender_id = event['sender']['id']
    payload = event['postback']['payload']

    if payload == 'GET_STARTED_PAYLOAD':
        send_instructions(sender_id)
    else:
        send_text_message(sender_id, 'Ooops, invalid postback!!!')
