from django.conf.urls.defaults import *

from cyder.cydhcp.range.views import *
from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = patterns(
    '',
    url(r'^find_range/', redirect_to_range_from_ip, name='range-find'),
    url(r'^(?P<range_pk>[\w-]+)/$', range_detail, name='range-detail'),
) + cydhcp_urls('range')
