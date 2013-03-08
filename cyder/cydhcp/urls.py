from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from cyder.cydhcp.views import (cydhcp_view, cydhcp_delete, table_update,
                                cydhcp_get_record, cydhcp_search_record,
                                cydhcp_create)


def cydhcp_urls(object_type):
    """Url generator for DHCP views"""
    return patterns('',
        url(r'^$', cydhcp_view, name=object_type),
        url(r'^create/$', cydhcp_create, name=object_type + '-create'),
        url(r'^(?P<pk>[\w-]+)/update/$', cydhcp_view,
            name=object_type + '-update'),
        url(r'^(?P<pk>[\w-]+)/delete/$', cydhcp_delete,
            name=object_type + '-delete'),
        url(r'^(?P<pk>[\w-]+)/tableupdate/$', table_update,
            name=object_type + '-table-update'),
    )


urlpatterns = patterns(
    '',
    url(r'^$', direct_to_template, {'template': 'cydhcp/cydhcp_index.html'},
        name='cydhcp-index'),
    url(r'^record/get/', cydhcp_get_record, name='cydhcp-get-record'),
    url(r'^record/search/', cydhcp_search_record, name='cydhcp-search-record'),
    url(r'^build/', include('cyder.cydhcp.build.urls')),
    url(r'^network/', include('cyder.cydhcp.network.urls')),
    url(r'^range/', include('cyder.cydhcp.range.urls')),
    url(r'^site/', include('cyder.cydhcp.site.urls')),
    url(r'^vlan/', include('cyder.cydhcp.vlan.urls')),
    url(r'^static_interface/',
        include('cyder.cydhcp.interface.static_intr.urls')),
    url(r'^dynamic_interface/',
        include('cyder.cydhcp.interface.dynamic_intr.urls')),
    url(r'^vrf/', include('cyder.cydhcp.vrf.urls')),
    url(r'^workgroup/', include('cyder.cydhcp.workgroup.urls')),
)
