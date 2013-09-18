from django.conf.urls.defaults import url, patterns

from cyder.cydhcp.range.views import (redirect_to_range_from_ip, range_detail,
                                      search)
from cyder.cydhcp.range.utils import range_wizard
from cyder.cydhcp.urls import cydhcp_urls


urlpatterns = cydhcp_urls('range') + patterns(
    '',
    url(r'^search/', search, name='range-search'),
    url(r'^range_wizard/', range_wizard, name='range-wizard'),
    url(r'^find_range/', redirect_to_range_from_ip, name='range-find'),
    url(r'^(?P<pk>[\w-]+)/$', range_detail, name='range-detail'),
)
