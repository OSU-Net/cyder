from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from cyder.cydns.api.v1.api import v1_dns_api
from cyder.cydns.views import cydns_search_record, cydns_update_record


urlpatterns = patterns('',
   url(r'^$', direct_to_template, {'template': 'cydns/cydns_index.html'},
       name='cydns-index'),
    url(r'^record/update/', cydns_update_record, name='cydns-update-record'),
    url(r'^record/search/', cydns_search_record, name='cydns-search-record'),

   url(r'^address_record/', include ('cyder.cydns.address_record.urls'),
       kwargs={'record_type': 'address_record'}),
   url(r'^cname/', include('cyder.cydns.cname.urls'),
       kwargs={'record_type': 'cname'}),
   url(r'^domain/', include('cyder.cydns.domain.urls'),
       kwargs={'record_type': 'domain'}),
   url(r'^mx/', include('cyder.cydns.mx.urls'),
       kwargs={'record_type': 'mx'}),
   url(r'^nameserver/', include('cyder.cydns.nameserver.urls'),
       kwargs={'record_type': 'nameserver'}),
   url(r'^ptr/', include('cyder.cydns.ptr.urls'),
       kwargs={'record_type': 'ptr'}),
   url(r'^soa/', include('cyder.cydns.soa.urls'),
       kwargs={'record_type': 'soa'}),
   url(r'^srv/', include('cyder.cydns.srv.urls'),
       kwargs={'record_type': 'srv'}),
   url(r'^txt/', include('cyder.cydns.txt.urls'),
       kwargs={'record_type': 'txt'}),

   url(r'^sshfp/', include('cyder.cydns.sshfp.urls')),
   url(r'^view/', include('cyder.cydns.view.urls')),
   url(r'^bind/', include('cyder.cydns.cybind.urls')),
   url(r'^api/', include(v1_dns_api.urls)),
)
