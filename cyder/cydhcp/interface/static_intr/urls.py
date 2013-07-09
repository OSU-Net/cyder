from django.conf.urls.defaults import patterns, url
from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.views import cydhcp_create
urlpatterns = patterns(
    '',
    url(r'^create/$', cydhcp_create,
        name='static_intr-create'),
) + cydhcp_urls('static_interface')
