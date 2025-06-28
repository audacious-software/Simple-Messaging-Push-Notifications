# pylint: disable=line-too-long

try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

from .views import simple_messaging_register_for_messages, simple_messaging_push_reply, simple_messaging_push_browser_register, simple_messaging_service_worker

urlpatterns = [
    url('register.json', simple_messaging_register_for_messages, name='simple_messaging_register_for_messages'),
    url('reply.json', simple_messaging_push_reply, name='simple_messaging_push_reply'),
    url('service-worker.js', simple_messaging_service_worker, name='simple_messaging_service_worker'),
    url('^$', simple_messaging_push_browser_register, name='simple_messaging_push_browser_register'),
]
