from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.domain.views import *
from cyder.cydns.views import cydns_list_create_record


urlpatterns = patterns('',
   url(r'^$', cydns_list_create_record, name='domain-list'),

   url(r'^get_all_domains/$', get_all_domains, name='get-all-domains'),

   url(r'(?P<pk>[\w-]+)/update/$',
       cydns_list_create_record, name='domain-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(DomainDeleteView.as_view()), name='domain-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(DomainDetailView.as_view()), name='domain-detail'),
)
