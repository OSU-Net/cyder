from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.nameserver.views import *
from cyder.cydns.views import cydns_list_create_record

urlpatterns = patterns('',
   url(r'^$', cydns_list_create_record, name='nameserver-list',
       kwargs={'record_type': 'nameserver'}),

   url(r'(?P<domain>[\w-]+)/create_delegated/$',
       csrf_exempt(create_ns_delegated), name='nameserver-delegated-create'),
   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(NSCreateView.as_view()), name='nameserver-by-domain-create'),

   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(NSUpdateView.as_view()), name='nameserver-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(NSDeleteView.as_view()), name='nameserver-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(NSDetailView.as_view()), name='nameserver-detail'),
)
