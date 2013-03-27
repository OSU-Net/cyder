from django.conf.urls.defaults import *

from cyder.cydhcp.network.views import *
from cyder.cydhcp.network.network_wizard import *
from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = cydhcp_urls('network') + patterns('',
    url(r'^wizard_create/$', network_wizard, name='network-wizard'),
    url(r'^(?P<pk>[\w-]+)/$', NetworkDetailView.as_view(), name='network-detail'),
)
