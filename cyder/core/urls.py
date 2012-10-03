from django.conf.urls.defaults import *

from cyder.core.interface.static_intr.views import create_static_interface
from cyder.core.interface.static_intr.views import edit_static_interface

from django.views.decorators.csrf import csrf_exempt

from cyder.core.views import search_ip
from cyder.core.search.views import search


urlpatterns = patterns('',
                       url(r'^$', csrf_exempt(search), name='core-index'),
                       url(r'^interface/', include('cyder.core.interface.urls')),
                       url(r'^vlan/', include('cyder.core.vlan.urls')),
                       url(r'^network/', include('cyder.core.network.urls')),
                       url(r'^site/', include('cyder.core.site.urls')),
                       url(r'^range/', include('cyder.core.range.urls')),
                       url(r'^build/', include('cyder.core.build.urls')),
                       url(r'^search/', include('cyder.core.search.urls')),
                       url(r'^bulk_change/', include('cyder.core.bulk_change.urls')),
                       )
