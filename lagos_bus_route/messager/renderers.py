from __future__ import unicode_literals


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
