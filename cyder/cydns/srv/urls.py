from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.srv.views import *
from cyder.cydns.views import cydns_list_create_record

urlpatterns = patterns('',
   url(r'^$', cydns_list_create_record, name='srv-list',
       kwargs={'record_type': 'SRV'}),
   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(SRVCreateView.as_view()), name='srv-create-in-domain'),
   url(r'create/$', csrf_exempt(SRVCreateView.as_view()), name='srv-create'),
   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(SRVUpdateView.as_view()), name='srv-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(SRVDeleteView.as_view()), name='srv-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(SRVDetailView.as_view()), name='srv-detail'),
)
