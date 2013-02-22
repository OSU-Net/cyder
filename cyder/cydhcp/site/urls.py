from django.conf.urls.defaults import *

from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.site.views import *


urlpatterns = patterns(
    '',
    url(r'^create/$', SiteCreateView.as_view(), name='site-create'),
    url(r'^(?P<site_pk>[\w-]+)/$', site_detail, name='site-detail'),
) + cydhcp_urls('site')
