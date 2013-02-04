from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.csrf import csrf_exempt

from cyder.cydhcp.interface.static_intr.views import (
                StaticInterfaceListView, StaticInterfaceDetailView,
                StaticInterfaceUpdateView, StaticInterfaceDeleteView,
                StaticInterfaceCreateView)

urlpatterns = patterns('',
        url(r'^$', csrf_exempt(StaticInterfaceListView.as_view()),
                name='static_interface-list'),
        url(r'(?P<pk>[\w-]+)/$',
                csrf_exempt(StaticInterfaceDetailView.as_view()),
                name='static_interface-detail'),
        url(r'update/(?P<pk>[\w-]+)/$',
                csrf_exempt(StaticInterfaceUpdateView.as_view()),
                name='static_interface-update'),
        url(r'delete/(?P<pk>[\w-]+)/$',
                csrf_exempt(StaticInterfaceDeleteView.as_view()),
                name='static_interface-delete'),
        url(r'create/$', csrf_exempt(StaticInterfaceCreateView.as_view()),
                name='static_interface-create'),
)
