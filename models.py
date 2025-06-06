from django.conf import settings

from django.core.checks import Error, Warning, register # pylint: disable=redefined-builtin

@register()
def check_credentials_json(app_configs, **kwargs): # pylint: disable=unused-argument
    errors = []

    if hasattr(settings, 'SIMPLE_MESSAGING_FIREBASE_CREDENTIALS_JSON') is False:
        error = Warning('SIMPLE_MESSAGING_FIREBASE_CREDENTIALS_JSON parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_FIREBASE_CREDENTIALS_JSON (path to Firebase service credentials JSON file).', obj=None, id='simple_messaging_push_notifications.W001')
        errors.append(error)

    return errors

@register()
def check_default_title(app_configs, **kwargs): # pylint: disable=unused-argument
    errors = []

    if hasattr(settings, 'SIMPLE_MESSAGING_DEFAULT_TITLE') is False:
        error = Error('SIMPLE_MESSAGING_DEFAULT_TITLE parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_DEFAULT_TITLE (default notification title).', obj=None, id='simple_messaging_push_notifications.E001')
        errors.append(error)

    return errors
