from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from cyder.cydhcp.workgroup.views import *
from django.views.decorators.csrf import csrf_exempt


urlpatterns = patterns('',
   url(r'^/$', csrf_exempt(WorkgroupListView.as_view()),
                        name='workgroup-list'),
   url(r'update/(?P<pk>[\w-]+)/$', csrf_exempt(WorkgroupUpdateView.as_view()),
                        name='workgroup-update'),
   url(r'delete/(?P<pk>[\w-]+)/$', csrf_exempt(WorkgroupDeleteView.as_view()),
                        name='workgroup-delete'),
   url(r'create/$', csrf_exempt(WorkgroupCreateView.as_view()),
                        name='workgroup-create'),
   url(r'(?P<pk>[\w-]+)/$', csrf_exempt(WorkgroupDetailView.as_view()),
                        name='workgroup-detail'),
)
