from django.conf.urls.defaults import *

from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.site.views import site_detail


urlpatterns = cydhcp_urls('site') + patterns('',
    url(r'^(?P<pk>[\w-]+)/$', site_detail, name='site-detail'),
)
