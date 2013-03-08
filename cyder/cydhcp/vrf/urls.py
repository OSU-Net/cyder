from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.vrf.views import vrf_detail
from django.conf.urls.defaults import url, patterns

# NEED TO FIX
urlpatterns = patterns(
    '',
    url(r'^(?P<vrf_pk>[\w-]+)/$', vrf_detail, name='vrf-detail'),
) + cydhcp_urls('vrf')
