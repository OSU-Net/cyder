from django.conf.urls.defaults import *

from cyder.cydns.views import *
from cyder.cydns.constants import DNS_KEY_VALUES


def cydns_urls(obj_type):
    """Url generator for DNS record views."""
    return patterns(
        '',
        url(r'^$', cydns_view, name=obj_type),
        url(r'(?P<pk>[\w-]+)/update/$', cydns_view,
            name=obj_type + '-update'),
        url(r'(?P<pk>[\w-]+)/delete/$', cydns_delete,
            name=obj_type + '-delete'),
        url(r'(?P<pk>[\w-]+)/tableupdate/$', cydns_table_update,
            name=obj_type + '-table-update'),
    )


urlpatterns = patterns(
    '',
    url(r'^$', cydns_index, name='cydns-index'),

    url(r'^record/get/', cydns_get_update_form, name='cydns-get-record'),
    url(r'^record/search/', cydns_search_obj, name='cydns-search-record'),

    url(r'^address_record/', include('cyder.cydns.address_record.urls')),
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
)
for kv in DNS_KEY_VALUES:
    urlpatterns += patterns(
        '',
        url(r"^{0}/".format(kv), include(cydns_urls(kv))))
