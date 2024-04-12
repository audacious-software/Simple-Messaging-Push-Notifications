# pylint: disable=line-too-long, no-member

import json
import os
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template import Template, Context

def process_outgoing_message(outgoing_message, metadata=None): # pylint: disable=too-many-branches, too-many-locals
    if metadata is None:
        metadata = {}

    # Likely local user ID, not addressable string. Lookup using custom implementation of
    #
    #   simple_messaging_api.update_message_metadata
    #
    # provided by an app in the local project. Should provide at least one of the
    # following custom metadata fields:
    #
    #   apns_ids: Array of device tokens for sending Apple push notifications
    #   fcm_ids: Array of device tokens for sending Firebase cloud messages (primarily to
    #            Android apps)

    destination = outgoing_message.current_destination()

    if outgoing_message.transmission_metadata is not None:
        try:
            transmission_metadata = json.loads(outgoing_message.transmission_metadata)

            if isinstance(transmission_metadata, dict):
                apns_ids = transmission_metadata.get('apns_ids', None)
                fcm_ids = transmission_metadata.get('fcm_ids', None)

                if apns_ids is not None or fcm_ids is not None:
                    # We have a push notification to send.

                    if apns_ids is not None:
                        pass # Talk to Apple API via HTTP/2 with HTTPX library: https://pypi.org/project/httpx/

                    if fcm_ids is not None:
                        pass # Talk to Firebase API via Firebase SDK: https://github.com/firebase/firebase-admin-python
            else:
                pass # Message doesn't appear to have the proper fields.


        except ValueError:
            pass # Message doesn't appear to have the proper fields.

    return None

def simple_messaging_media_enabled(outgoing_message): # pylint: disable=unused-argument
    destination = outgoing_message.current_destination()

    return re.fullmatch(EMAIL_REGEX, destination)

def process_incoming_request(request): # pylint: disable=unused-argument
    return HttpResponse('Not implemented', status_code=501, content_type='text/plain')
