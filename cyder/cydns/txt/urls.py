from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.txt.views import *
from cyder.cydns.views import cydns_list_create_record

urlpatterns = patterns('',
   url(r'^$', cydns_list_create_record, name='txt-list',
       kwargs={'record_type': 'TXT'}),
   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(TXTCreateView.as_view()), name='txt-create-in-domain'),
   url(r'create/$', csrf_exempt(TXTCreateView.as_view()), name='txt-create'),
   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(TXTUpdateView.as_view()), name='txt-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(TXTDeleteView.as_view()), name='txt-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(TXTDetailView.as_view()), name='txt-detail'),
   )
