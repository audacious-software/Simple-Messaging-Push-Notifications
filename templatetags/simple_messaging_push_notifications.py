# pylint: disable=line-too-long, no-member

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import mark_safe
from django.urls import reverse

register = template.Library()

@register.simple_tag()
def simple_messaging_push_browser_register(identifier):
    template_context = {
        'registration_url': reverse('simple_messaging_register_for_messages'),
        'identifier': identifier,
        'public_key': settings.SIMPLE_MESSAGING_WEB_PUBLIC_KEY,
    }

    try:
        template_context['app_name'] = settings.SIMPLE_MESSAGING_PUSH_APP_NAME
    except AttributeError:
        template_context['app_name'] = 'Simple Messaging'

    return render_to_string('simple_messaging/browser_registration_template_tag.html', template_context)

