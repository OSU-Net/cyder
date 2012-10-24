from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from cyder.cydhcp.interface.static_intr.views import create_static_interface
from cyder.cydhcp.interface.static_intr.views import edit_static_interface

from django.views.decorators.csrf import csrf_exempt

from cyder.cydhcp.views import search_ip


urlpatterns = patterns('',
   url(r'^$', direct_to_template, {'template': 'cydhcp/cydhcp_base.html'}, name='cydhcp-index'),
   url(r'^interface/', include('cyder.cydhcp.interface.urls')),
   url(r'^vlan/', include('cyder.cydhcp.vlan.urls')),
   url(r'^network/', include('cyder.cydhcp.network.urls')),
   url(r'^site/', include('cyder.cydhcp.site.urls')),
   url(r'^range/', include('cyder.cydhcp.range.urls')),
   url(r'^build/', include('cyder.cydhcp.build.urls')),
   url(r'^bulk_change/', include('cyder.cydhcp.bulk_change.urls')),
)
