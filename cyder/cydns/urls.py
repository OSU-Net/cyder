from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from cyder.cydns.api.v1.api import v1_dns_api
from cyder.cydns.views import *


def cydns_urls(record_type):
    """Url generator for DNS record views."""
    return patterns('',
        url(r'^$', cydns_view, name=record_type),
        url(r'(?P<pk>[\w-]+)/update/$', cydns_view,
            name=record_type + '-update'),
        url(r'(?P<pk>[\w-]+)/delete/$', cydns_delete,
            name=record_type + '-delete'),
        url(r'(?P<pk>[\w-]+)/tableupdate/$', table_update,
            name=record_type + '-table-update'),
    )


urlpatterns = patterns('',
   url(r'^$', direct_to_template, {'template': 'cydns/cydns_index.html'},
       name='cydns-index'),

   url(r'^record/get/', cydns_get_record, name='cydns-get-record'),
   url(r'^record/search/', cydns_search_record, name='cydns-search-record'),

   url(r'^address_record/', include ('cyder.cydns.address_record.urls')),
   url(r'^cname/', include('cyder.cydns.cname.urls')),
   url(r'^domain/', include('cyder.cydns.domain.urls')),
   url(r'^mx/', include('cyder.cydns.mx.urls')),
   url(r'^nameserver/', include('cyder.cydns.nameserver.urls')),
   url(r'^ptr/', include('cyder.cydns.ptr.urls')),
   url(r'^soa/', include('cyder.cydns.soa.urls')),
   url(r'^srv/', include('cyder.cydns.srv.urls')),
   url(r'^txt/', include('cyder.cydns.txt.urls')),
   url(r'^sshfp/', include('cyder.cydns.sshfp.urls')),

   url(r'^view/', include('cyder.cydns.view.urls')),
   url(r'^bind/', include('cyder.cydns.cybind.urls')),
   url(r'^api/', include(v1_dns_api.urls)),
)
