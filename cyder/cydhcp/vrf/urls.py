from django.conf.urls.defaults import url, patterns

from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.vrf.views import vrf_detail


urlpatterns = cydhcp_urls('vrf') + patterns('',
    url(r'^(?P<pk>[\w-]+)/$', vrf_detail, name='vrf-detail'),
) + cydhcp_urls('vrf_kv')
