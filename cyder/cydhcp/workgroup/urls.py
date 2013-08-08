from django.conf.urls.defaults import url, patterns

from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.workgroup.views import search

urlpatterns = cydhcp_urls('workgroup') + patterns(
    '',
    url(r'^search/', search, name='workgroup-search'),
)
