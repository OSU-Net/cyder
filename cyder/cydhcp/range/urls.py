from django.conf.urls.defaults import *

from cyder.cydhcp.range.views import redirect_to_range_from_ip, range_detail
from cyder.cydhcp.urls import cydhcp_urls


urlpatterns = cydhcp_urls('range') + patterns('',
    url(r'^find_range/', redirect_to_range_from_ip, name='range-find'),
    url(r'^(?P<pk>[\w-]+)/$', range_detail, name='range-detail'),
) + cydhcp_urls('range_kv')
