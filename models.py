from django.conf import settings

from django.core.checks import Error, Warning, register # pylint: disable=redefined-builtin

@register()
def check_firebase_push_setup(app_configs, **kwargs): # pylint: disable=unused-argument
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

@register()
def check_apple_push_setup(app_configs, **kwargs): # pylint: disable=unused-argument
    errors = []

    if hasattr(settings, 'SIMPLE_MESSAGING_APNS_CERTIFICATE') is False:
        error = Warning('SIMPLE_MESSAGING_APNS_CERTIFICATE parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_APNS_CERTIFICATE (certificate file path).', obj=None, id='simple_messaging_push_notifications.W002')
        errors.append(error)

    if hasattr(settings, 'SIMPLE_MESSAGING_APNS_KEY') is False:
        error = Warning('SIMPLE_MESSAGING_APNS_KEY parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_APNS_KEY (key file path).', obj=None, id='simple_messaging_push_notifications.W003')
        errors.append(error)

    if hasattr(settings, 'SIMPLE_MESSAGING_APNS_PASSWORD') is False:
        error = Warning('SIMPLE_MESSAGING_APNS_PASSWORD parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_APNS_PASSWORD (key file password).', obj=None, id='simple_messaging_push_notifications.W004')
        errors.append(error)

    if hasattr(settings, 'SIMPLE_MESSAGING_APNS_URL') is False:
        error = Warning('SIMPLE_MESSAGING_APNS_URL parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_APNS_URL (production URL).', obj=None, id='simple_messaging_push_notifications.W005')
        errors.append(error)

    if hasattr(settings, 'SIMPLE_MESSAGING_APNS_URL_SANDBOX') is False:
        error = Warning('SIMPLE_MESSAGING_APNS_URL_SANDBOX parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_APNS_URL_SANDBOX (sandbox URL).', obj=None, id='simple_messaging_push_notifications.W006')
        errors.append(error)

    if hasattr(settings, 'SIMPLE_MESSAGING_APNS_URL_SANDBOX') is False:
        error = Warning('SIMPLE_MESSAGING_APNS_URL_SANDBOX parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_APNS_URL_SANDBOX (sandbox URL).', obj=None, id='simple_messaging_push_notifications.W006')
        errors.append(error)

    if hasattr(settings, 'SIMPLE_MESSAGING_WEB_PRIVATE_KEY') is False:
        error = Warning('SIMPLE_MESSAGING_WEB_PRIVATE_KEY parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_WEB_PRIVATE_KEY (VAPID private key).', obj=None, id='simple_messaging_push_notifications.W007')
        errors.append(error)

    if hasattr(settings, 'SIMPLE_MESSAGING_WEB_PRIVATE_KEY') is False:
        error = Warning('SIMPLE_MESSAGING_WEB_SUBJECT parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_WEB_SUBJECT (web notification subject).', obj=None, id='simple_messaging_push_notifications.W008')
        errors.append(error)

    if hasattr(settings, 'SIMPLE_MESSAGING_WEB_PRIVATE_KEY') is False:
        error = Warning('SIMPLE_MESSAGING_WEB_SUBJECT parameter not defined', hint='Update configuration to include SIMPLE_MESSAGING_WEB_SUBJECT (web notification subject).', obj=None, id='simple_messaging_push_notifications.W008')
        errors.append(error)

    return errors
