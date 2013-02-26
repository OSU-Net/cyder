from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.vrf.views import VrfCreateView, vrf_detail
from django.conf.urls.defaults import url, patterns

# NEED TO FIX
urlpatterns = patterns(
    '',
    url(r'^create/$', VrfCreateView.as_view(),
        name='vrf-create'),
    url(r'^(?P<vrf_pk>[\w-]+)/$', vrf_detail, name='vrf-detail'),
) + cydhcp_urls('vrf')
