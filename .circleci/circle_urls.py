# pylint: disable=no-name-in-module

import sys

import django

if sys.version_info[0] > 2:
    from django.urls import include, re_path

    urlpatterns = [
        re_path(r'^admin/', django.contrib.admin.site.urls),
        re_path(r'^messages/', include('simple_messaging.urls')),
        re_path(r'^messages/push/', include('simple_messaging_push_notifications.urls')),
    ]
else:
    from django.conf.urls import include, url

    urlpatterns = [
        url(r'^admin/', django.contrib.admin.site.urls),
        url(r'^messages/', include('simple_messaging.urls')),
        url(r'^messages/push/', include('simple_messaging_push_notifications.urls')),
    ]
