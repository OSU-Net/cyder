from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.nameserver.views import *
from cyder.cydns.urls import cydns_urls


urlpatterns = cydns_urls('nameserver')


urlpatterns += patterns('',
   url(r'(?P<domain>[\w-]+)/create_delegated/$',
       csrf_exempt(create_ns_delegated), name='nameserver-delegated-create'),
   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(NSCreateView.as_view()), name='nameserver-by-domain-create'),
)
