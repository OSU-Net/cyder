from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.mozdns.nameserver.views import *

urlpatterns = patterns('',
   url(r'^$', NSListView.as_view(), name='nameserver-list'),
   url(r'(?P<domain>[\w-]+)/create_delegated/$',
       csrf_exempt(create_ns_delegated), name='nameserver-delegated-create'),
   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(NSCreateView.as_view()), name='nameserver-by-domain-create'),
   url(r'create/$', csrf_exempt(NSCreateView.as_view()), name='nameserver-create'),
   url(r'(?P<nameserver_pk>[\w-]+)/update/$',
       csrf_exempt(update_ns), name='nameserver-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(NSDeleteView.as_view()), name='nameserver-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(NSDetailView.as_view()), name='nameserver-detail'),
)
