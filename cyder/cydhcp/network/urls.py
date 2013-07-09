from django.conf.urls.defaults import *

from cyder.cydhcp.network.views import network_detail
from cyder.cydhcp.network.network_wizard import network_wizard
from cyder.cydhcp.urls import cydhcp_urls


urlpatterns = cydhcp_urls('network') + patterns(
    '',
    url(r'^wizard/$', network_wizard, name='network-wizard'),
    url(r'^(?P<pk>[\w-]+)/$', network_detail, name='network-detail'),
)
