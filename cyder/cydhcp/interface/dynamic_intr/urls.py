from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.csrf import csrf_exempt
from cyder.cydhcp.interface.dynamic_intr.views import (
                DynamicInterfaceListView, DynamicInterfaceDetailView,
                DynamicInterfaceUpdateView, DynamicInterfaceDeleteView,
                DynamicInterfaceCreateView)
from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = patterns('',
    url(r'create/$', csrf_exempt(DynamicInterfaceCreateView.as_view()),
                    name='dynamic_interface-create'),
    url(r'(?P<pk>[\w-]+)/$',
                    csrf_exempt(DynamicInterfaceDetailView.as_view()),
                    name='dynamic_interface-details'),
) + cydhcp_urls('dynamic_intr')
