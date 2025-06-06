try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

from .views import register_for_messages, simple_messaging_push_reply

urlpatterns = [
    url('register.json', register_for_messages, name='register_for_messages'),
    url('reply.json', simple_messaging_push_reply, name='simple_messaging_push_reply'),
]
