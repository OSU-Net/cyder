from django.conf.urls.defaults import patterns, url
from cyder.cydhcp.interface.dynamic_intr.views import (
    DynamicInterfaceDetailView)
from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.views import cydhcp_create

urlpatterns = patterns('',
                       url(r'create/$',
                           cydhcp_create,
                           name='dynamic_interface-create'),
                       url(r'(?P<pk>[\w-]+)/$',
                           DynamicInterfaceDetailView.as_view(),
                           name='dynamic_interface-details'),)
urlpatterns += cydhcp_urls('dynamic_interface')
