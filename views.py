# pylint: disable=line-too-long, no-member

import importlib
import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from simple_messaging.models import IncomingMessage

@csrf_exempt
def simple_messaging_register_for_messages(request): # pylint: disable=too-many-branches, invalid-name
    identifier = request.POST.get('identifier', request.GET.get('identifier', None))
    platform = request.POST.get('platform', request.GET.get('platform', None))
    token = request.POST.get('token', request.GET.get('token', None))

    print('simple_messaging_register_for_messages: %s -- %s -- %s', identifier, platform, token)

    if token is None:
        subscription = request.POST.get('subscription', request.GET.get('subscription', None))

        token = json.loads(subscription)

    if None in (identifier, platform, token,):
        payload = {
            'error': 'Missing full registration payload. Verify that "identifier", "platform", and "token" are all present.'
        }

        return HttpResponse(json.dumps(payload, indent=2), content_type='application/json', status=400)

    registered = False

    for app in settings.INSTALLED_APPS:
        try:
            message_module = importlib.import_module('.simple_messaging_api', package=app)

            if message_module.simple_messaging_register_push_token(identifier, platform, token):
                registered = True
        except ImportError:
            pass
        except AttributeError:
            pass

    if registered:
        payload = {
            'message': 'Token registered successfully.',
            'success': True
        }

        return HttpResponse(json.dumps(payload, indent=2), content_type='application/json', status=200)

    payload = {
        'error': 'Unable to register token. Verify that the server is configured correctly with at least one app for token registration.'
    }

    return HttpResponse(json.dumps(payload, indent=2), content_type='application/json', status=500)

@csrf_exempt
def simple_messaging_push_reply(request): # pylint: disable=too-many-branches
    identifier = request.POST.get('identifier', request.GET.get('identifier', None))
    platform = request.POST.get('platform', request.GET.get('platform', None))
    responding_to = request.POST.get('responding_to', request.GET.get('responding_to', None))
    response = request.POST.get('response', request.GET.get('response', None))

    metadata = {
        'identifier': identifier,
        'platform': platform,
        'responding_to': responding_to,
        'response': response,
    }

    new_incoming = IncomingMessage.objects.create(sender=identifier, recipient=platform, receive_date=timezone.now(), message=response, transmission_metadata=json.dumps(metadata, indent=2))
    new_incoming.encrypt_sender()

    payload = {
        'message': 'Response recorded successfully.',
        'success': True
    }

    return HttpResponse(json.dumps(payload, indent=2), content_type='application/json', status=200)

#    payload = {
#        'error': 'Unable to register token. Verify that the server is configured correctly with at least one app for token registration.'
#    }
#
#    return HttpResponse(json.dumps(payload, indent=2), content_type='application/json', status=500)

def simple_messaging_push_browser_register(request): # pylint: disable=invalid-name
    return render(request, 'simple_messaging/browser_registration.html', status=200)

def simple_messaging_service_worker(request):
    response = render(request, 'simple_messaging/browser_registration_service_worker.js', content_type='text/javascript', status=200)
    response['Service-Worker-Allowed'] = '/'

    return response
