from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('',
   url(r'^$', direct_to_template, {'template': 'cydhcp/cydhcp_base.html'},
       name='cydhcp-index'),
   url(r'^interface/', include('cyder.cydhcp.interface.urls')),
   url(r'^network/', include('cyder.cydhcp.network.urls')),
   url(r'^range/', include('cyder.cydhcp.range.urls')),
   url(r'^site/', include('cyder.cydhcp.site.urls')),
   url(r'^vlan/', include('cyder.cydhcp.vlan.urls')),
)
