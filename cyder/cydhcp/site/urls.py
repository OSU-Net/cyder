from django.conf.urls.defaults import *

from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.site.views import *


urlpatterns = cydhcp_urls('site') + patterns('',
    url(r'^(?P<site_pk>[\w-]+)/$', site_detail, name='site-detail'),
)
