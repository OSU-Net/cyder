from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.domain.views import *
from cyder.cydns.views import cydns_list_create_record

urlpatterns = patterns('',
   url(r'^$', DomainListView.as_view(), name='domain-list'),
   url(r'^reverse_domains/$',
       ReverseDomainListView.as_view(), name='reverse_domain-list'),
   url(r'^get_all_domains/$', get_all_domains, name='get-all-domains'),
   url(r'create/$', csrf_exempt(
       DomainCreateView.as_view()), name='domain-create'),
   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(DomainUpdateView.as_view()), name='domain-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(DomainDeleteView.as_view()), name='domain-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(DomainDetailView.as_view()), name='domain-detail'),
)
