from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.cname.views import *
from cyder.cydns.views import cydns_list_create_view

urlpatterns = patterns('',
   url(r'^$', cydns_list_create_view, name='cname-list',
       kwargs={'record_type': 'CNAME'}),
   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(CNAMECreateView.as_view()), name='cname-create-in-domain'),
   url(r'create/$', csrf_exempt(CNAMECreateView.as_view()), name='cname-create'),
   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(CNAMEUpdateView.as_view()), name='cname-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(CNAMEDeleteView.as_view()), name='cname-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(CNAMEDetailView.as_view()), name='cname-detail'),
)
