from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from cyder.cydhcp.workgroup.views import *
from django.views.decorators.csrf import csrf_exempt
from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = patterns('',
    url(r'create/$', WorkgroupCreateView.as_view(),
        name='workgroup-create'),
    url(r'(?P<pk>[\w-]+)/$', WorkgroupDetailView.as_view(),
        name='workgroup-detail'),
) + cydhcp_urls('workgroup')
