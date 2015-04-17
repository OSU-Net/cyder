from django.conf.urls.defaults import patterns, url

from cyder.cydhcp.supernet.views import supernet_detail
from cyder.cydhcp.urls import cydhcp_urls


urlpatterns = cydhcp_urls('supernet') + patterns(
    '',
    url(r'^(?P<pk>[\w-]+)/$', supernet_detail, name='supernet-detail'),
)
