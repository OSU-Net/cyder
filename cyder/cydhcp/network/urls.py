from django.conf.urls.defaults import *

from cyder.cydhcp.network.views import *
from cyder.cydhcp.network.network_wizard import *
from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = patterns(
    '',
    url(r'^wizard_create/$', network_wizard, name='network-wizard'),
    url(r'^create/$', create_network, name='network-create'),
    url(r'^(?P<network_pk>[\w-]+)/$', network_detail, name='network-detail'),
) + cydhcp_urls('network')
