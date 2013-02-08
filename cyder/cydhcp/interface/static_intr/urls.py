from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.csrf import csrf_exempt
from cyder.cydhcp.interface.static_intr.views import (
                StaticInterfaceListView, StaticInterfaceDetailView,
                StaticInterfaceUpdateView, StaticInterfaceDeleteView,
                StaticInterfaceCreateView)
from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = patterns('',
        url(r'(?P<pk>[\w-]+)/$',
                csrf_exempt(StaticInterfaceDetailView.as_view()),
                name='static_interface-detail'),
        url(r'create/$', csrf_exempt(StaticInterfaceCreateView.as_view()),
                name='static_interface-create'),
) + cydhcp_urls('static_interface')
