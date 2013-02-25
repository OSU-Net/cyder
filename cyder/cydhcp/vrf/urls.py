from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.vrf.views import VrfCreateView
from django.conf.urls.defaults import url, patterns

# NEED TO FIX
urlpatterns = patterns(
    '',
    url(r'^create/$', VrfCreateView.as_view(),
        name='vrf-create'),
) + cydhcp_urls('vrf')
