from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.csrf import csrf_exempt
from cyder.cydhcp.interface.dynamic_intr.views import (
                DynamicInterfaceListView, DynamicInterfaceDetailView,
                DynamicInterfaceUpdateView, DynamicInterfaceDeleteView,
                DynamicInterfaceCreateView)

urlpatterns = patterns('',
    url(r'^$', csrf_exempt(DynamicInterfaceListView.as_view()),
                    name='dynamic_interface-list'),
    url(r'create/$', csrf_exempt(DynamicInterfaceCreateView.as_view()),
                    name='dynamic_interface-create'),
    url(r'(?P<pk>[\w-]+)/$',
                    csrf_exempt(DynamicInterfaceDetailView.as_view()),
                    name='dynamic_interface-details'),
    url(r'update/(?P<pk>[\w-]+)/$',
                    csrf_exempt(DynamicInterfaceUpdateView.as_view()),
                    name='dynamic_interface-update'),
    url(r'delete/(?P<pk>[\w-]+)/$',
                    csrf_exempt(DynamicInterfaceDeleteView.as_view()),
                    name='dynamic_interface-delete'),
)
