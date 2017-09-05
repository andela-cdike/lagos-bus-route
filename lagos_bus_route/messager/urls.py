from django.conf.urls import include, url

import views


urlpatterns = [
    url(r'webhook/$', views.Webhook.as_view(), name='webhook'),
]
