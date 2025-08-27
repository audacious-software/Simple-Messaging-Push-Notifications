# pylint: disable=line-too-long, no-member

import importlib
import json
import logging
import ssl
import traceback
import uuid

import aioapns
import firebase_admin
import httpx
import pywebpush

from firebase_admin import messaging

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

def process_outgoing_message(outgoing_message, metadata=None): # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    if metadata is None:
        metadata = {
            'tokens_to_clear': []
        }

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

    tokens = {}

    module_tokens = []

    for app in settings.INSTALLED_APPS: # pylint: disable=too-many-nested-blocks
        try:
            message_module = importlib.import_module('.simple_messaging_api', package=app)

            module_tokens = message_module.simple_messaging_fetch_tokens(destination)

            if module_tokens is not None:
                for channel, token_list in module_tokens.items():
                    channel_tokens = tokens.get(channel, [])

                    for token in token_list:
                        if (token in channel_tokens) is False:
                            channel_tokens.append(token)

                    tokens[channel] = channel_tokens
        except ImportError:
            pass
        except AttributeError:
            pass

    transmitted = False

    for channel, tokens in module_tokens.items():
        for app in settings.INSTALLED_APPS:
            try:
                message_module = importlib.import_module('.simple_messaging_api', package=app)

                new_metadata = message_module.simple_messaging_push_message(channel, tokens, outgoing_message)

                if new_metadata is not None:
                    channel_key = 'simple_messaging_push_notifications__%s' % channel

                    if (channel_key in metadata) is False:
                        metadata[channel_key] = {}

                    to_clear = new_metadata.get('tokens_to_clear', [])

                    metadata['tokens_to_clear'].extend(to_clear)

                    del new_metadata['tokens_to_clear']

                    metadata[channel_key].update(new_metadata)

                    transmitted = True
            except ImportError:
                pass
            except AttributeError:
                pass

    to_clear = metadata.get('tokens_to_clear', [])

    logging.info('to_clear = %s', to_clear)

    if len(to_clear) > 0:
        for app in settings.INSTALLED_APPS:
            try:
                message_module = importlib.import_module('.simple_messaging_api', package=app)

                message_module.simple_messaging_clear_tokens(destination, to_clear)
            except ImportError:
                pass
            except AttributeError:
                pass

    del metadata['tokens_to_clear']

    if transmitted is False:
        metadata['error'] = 'Unable to find push notification channels to transmit message.'
        outgoing_message.errored = True

    return metadata

async def send_ios_notification(token, outgoing_message, notification_id):
    message_text = outgoing_message.fetch_message()

    apn_payload = {
        'aps': {
            'alert': message_text,
            'badge': '1',
        }
    }

    apns_cert_client = aioapns.APNs(client_cert=settings.APPLE_PUSH_NOTIFICATION_CERTIFICATE, use_sandbox=settings.APPLE_PUSH_NOTIFICATION_USE_SANDBOX)

    apns_key_client = aioapns.APNs(key=settings.APPLE_PUSH_NOTIFICATION_KEY, key_id=settings.APPLE_PUSH_NOTIFICATION_KEY_ID, team_id=settings.APPLE_PUSH_NOTIFICATION_TEAM_ID, topic=settings.APPLE_PUSH_NOTIFICATION_TOPIC, use_sandbox=settings.APPLE_PUSH_NOTIFICATION_USE_SANDBOX)

    request = aioapns.NotificationRequest(device_token=token, message=apn_payload, notification_id=notification_id, push_type=aioapns.PushType.ALERT)

    await apns_cert_client.send_notification(request)
    await apns_key_client.send_notification(request)

def simple_messaging_push_message(channel, tokens, outgoing_message): # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    metadata = {
        'tokens_to_clear': []
    }

    try:
        metadata.update(json.loads(outgoing_message.message_metadata))
    except json.decoder.JSONDecodeError:
        pass

    push_metadata = metadata.get('push_notification', {})

    notification_ids = metadata.get('notification_ids', [])

    reply_url =  '%s%s' % (settings.SITE_URL, reverse('simple_messaging_push_reply'),)

    message_text = outgoing_message.fetch_message()

    try:
        if channel == 'ios':
            for token in tokens:
                notification_id = str(uuid.uuid4())

                notification_ids.append(notification_id)

                verify_context = ssl.create_default_context()
                verify_context.load_cert_chain(settings.SIMPLE_MESSAGING_APNS_CERTIFICATE, keyfile=settings.SIMPLE_MESSAGING_APNS_KEY, password=settings.SIMPLE_MESSAGING_APNS_PASSWORD)

                with httpx.Client(http2=True, verify=verify_context, timeout=60) as client:
                    headers = {
                        'apns-id': notification_id,
                        'apns-topic': 'edu.harvard.srl.SARA.V2.audacious',
                    }

                    payload = {
                        'aps': {
                            'alert': {
                                'title': push_metadata.get('title', settings.SIMPLE_MESSAGING_DEFAULT_TITLE),
                                'body': message_text,
                            },
                            'category' : 'SimpleMessaging',
                            'mutable-content': 1,
                            # "content-available" : 1,
                        },
                        'report_url': reply_url,
                        'report_reporter': outgoing_message.current_destination(),
                        'report_responding_to': 'OutgoingMessage:%d' % outgoing_message.pk,
                        'send_timestamp': timezone.now().isoformat(),
                    }

                    if outgoing_message.media.count() > 0:
                        for media_obj in outgoing_message.media.all():
                            if media_obj.content_type.startswith('image/'):
                                payload['image_url'] = '%s%s' % (settings.SITE_URL, media_obj.content_file.url)

                    positive_option = push_metadata.get('positive_option', None)

                    if positive_option is not None:
                        payload['include_positive_response'] = positive_option

                    negative_option = push_metadata.get('negative_option', None)

                    if negative_option is not None:
                        payload['include_negative_response'] = negative_option

                    neutral_option = push_metadata.get('neutral_option', None)

                    if neutral_option is not None:
                        payload['include_ok_response'] = neutral_option

                    sent_okay = False

                    for base_url in [settings.SIMPLE_MESSAGING_APNS_URL, settings.SIMPLE_MESSAGING_APNS_URL_SANDBOX]:
                        send_url = base_url + token

                        response = client.post(send_url, json=payload, headers=headers)

                        logger.info('resp: %s', response)
                        logger.info('status: %s', response.status_code)
                        logger.info('header: %s', dict(response.headers))
                        logger.info('body: %s', response.content)

                        if response.status_code == 200:
                            sent_okay = True

                        if metadata.get('notification_ids', None) is None:
                            metadata['notification_ids'] = []

                        metadata['notification_ids'].append(dict(response.headers))

                    if sent_okay is False:
                        metadata['tokens_to_clear'].append(token)

        elif channel == 'android':
            try:
                firebase_admin.get_app()
            except ValueError:
                credentials = firebase_admin.credentials.Certificate(settings.SIMPLE_MESSAGING_FIREBASE_CREDENTIALS_JSON)
                firebase_admin.initialize_app(credentials)

            payload = {
                'title': push_metadata.get('title', settings.SIMPLE_MESSAGING_DEFAULT_TITLE),
                'message': message_text,
                'report_url': reply_url,
                'report_reporter': outgoing_message.current_destination(),
                'report_responding_to': 'OutgoingMessage:%d' % outgoing_message.pk,
            }

            if outgoing_message.media.count() > 0:
                for media_obj in outgoing_message.media.all():
                    if media_obj.content_type.startswith('image/'):
                        payload['image_url'] = '%s%s' % (settings.SITE_URL, media_obj.content_file.url)

            positive_option = push_metadata.get('positive_option', None)

            if positive_option is not None:
                payload['include_positive_response'] = positive_option

            negative_option = push_metadata.get('negative_option', None)

            if negative_option is not None:
                payload['include_negative_response'] = negative_option

            neutral_option = push_metadata.get('neutral_option', None)

            if neutral_option is not None:
                payload['include_ok_response'] = neutral_option

            for token in tokens:
                message = messaging.Message(data=payload, token=token)

                try:
                    notification_id = messaging.send(message)

                    notification_ids.append(notification_id)

                    metadata['notification_ids'] = notification_ids
                except firebase_admin.exceptions.InvalidArgumentError:
                    metadata['tokens_to_clear'].append(token)

        elif channel == 'web':
            payload = {
                'title': push_metadata.get('title', settings.SIMPLE_MESSAGING_DEFAULT_TITLE),
                'message': message_text,
                'report_url': reply_url,
                'report_reporter': outgoing_message.current_destination(),
                'report_responding_to': 'OutgoingMessage:%d' % outgoing_message.pk,
            }

            if outgoing_message.media.count() > 0:
                for media_obj in outgoing_message.media.all():
                    if media_obj.content_type.startswith('image/'):
                        payload['image_url'] = '%s%s' % (settings.SITE_URL, media_obj.content_file.url)

            positive_option = push_metadata.get('positive_option', None)

            if positive_option is not None:
                payload['include_positive_response'] = positive_option

            negative_option = push_metadata.get('negative_option', None)

            if negative_option is not None:
                payload['include_negative_response'] = negative_option

            neutral_option = push_metadata.get('neutral_option', None)

            if neutral_option is not None:
                payload['include_ok_response'] = neutral_option

            url = push_metadata.get('url', None)

            if url is not None:
                payload['url'] = url

            for token in tokens:
                try:
                    response = pywebpush.webpush(token, json.dumps(payload), vapid_private_key=settings.SIMPLE_MESSAGING_WEB_PRIVATE_KEY, vapid_claims={
                        'sub': settings.SIMPLE_MESSAGING_WEB_SUBJECT
                    })
                except pywebpush.WebPushException:
                    traceback.print_exc()

                # notification_ids.append(notification_id)

                # metadata['notification_ids'] = notification_ids
    except: # pylint: disable=bare-except
        traceback.print_exc()

    return metadata

def annotate_messsage(outgoing, request):
    message_metadata = {}

    try:
        if outgoing.message_metadata is not None:
            message_metadata = json.loads(outgoing.message_metadata)
    except json.JSONDecodeError:
        pass

    push_details = {}

    title = request.get('push_notification_title', None)

    if title is not None:
        push_details['title'] = title

    positive_option = request.get('push_notification_positive_option', None)

    if positive_option is not None:
        push_details['positive_option'] = positive_option

    negative_option = request.get('push_notification_negative_option', None)

    if negative_option is not None:
        push_details['negative_option'] = negative_option

    neutral_option = request.get('push_notification_neutral_option', None)

    if neutral_option is not None:
        push_details['neutral_option'] = neutral_option

    if push_details:
        message_metadata['push_notification'] = push_details

        outgoing.message_metadata = json.dumps(message_metadata, indent=2)
        outgoing.save()

def process_incoming_request(request): # pylint: disable=unused-argument
    return HttpResponse('Not implemented', status_code=501, content_type='text/plain')

def simple_messaging_custom_console_ui(context): # pylint: disable=invalid-name
    include_ui = True

    try:
        from simple_messaging_switchboard.models import Channel, ChannelType  # pylint: disable=import-outside-toplevel

        loopback_type = ChannelType.objects.filter(package_name='simple_messaging_loopback').first()

        if loopback_type is not None:
            enabled_channel = Channel.objects.filter(channel_type__package_name='simple_messaging_loopback', is_enabled=True).first()

            if enabled_channel is None:
                include_ui = False

    except ImportError:
        pass

    if include_ui:
        return render_to_string("simple_messaging/console_push_notifications.html", context)

    return None
