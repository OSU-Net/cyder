from django.conf.urls.defaults import patterns, url

from cyder.cydhcp.network.views import network_detail
from cyder.cydhcp.urls import cydhcp_urls


urlpatterns = cydhcp_urls('network') + patterns(
    '',
    url(r'^(?P<pk>[\w-]+)/$', network_detail, name='network-detail'),
)
