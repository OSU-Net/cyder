from django.conf.urls.defaults import patterns, url

from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.workgroup.views import *


urlpatterns = cydhcp_urls('workgroup')
urlpatterns += patterns('',
    url(r'^(?P<pk>[\w-]+)/$', WorkgroupDetailView.as_view(),
        name='workgroup-detail'),
)
