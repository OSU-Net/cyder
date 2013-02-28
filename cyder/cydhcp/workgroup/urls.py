from django.conf.urls.defaults import patterns, url
from cyder.cydhcp.workgroup.views import *
from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = patterns(
    '',
    url(r'create/$', WorkgroupCreateView.as_view(),
        name='workgroup-create'),
    url(r'(?P<pk>[\w-]+)/$', WorkgroupDetailView.as_view(),
        name='workgroup-detail'),
) + cydhcp_urls('workgroup')
