from django.conf.urls.defaults import *

from cyder.cydhcp.site.views import *

urlpatterns = patterns('',
   url(r'^$', SiteListView.as_view(), name='site-list'),
   url(r'^create/$', SiteCreateView.as_view(), name='site-create'),
   url(r'^(?P<site_pk>[\w-]+)/$', site_detail, name='site-detail'),
   url(r'^(?P<site_pk>[\w-]+)/update/$', update_site, name='site-update'),
   url(r'^(?P<pk>[\w-]+)/delete/$',
       SiteDeleteView.as_view(), name='site-delete'),
)
