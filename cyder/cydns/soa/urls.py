from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.soa.views import *
from cyder.cydns.urls import cydns_urls


urlpatterns = cydns_urls('soa')


urlpatterns += patterns('',
   url(r'attr/$', delete_soa_attr, name='soa-attr'),

   url(r'create/$', csrf_exempt(SOACreateView.as_view()), name='soa-create'),
   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(SOAUpdateView.as_view()), name='soa-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(SOADeleteView.as_view()), name='soa-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(SOADetailView.as_view()), name='soa-detail'),
)
