from django.conf.urls.defaults import *

from core.interface.static_intr.views import create_static_interface
from core.interface.static_intr.views import edit_static_interface

from django.views.decorators.csrf import csrf_exempt

from core.views import search_ip
from core.search.views import search


urlpatterns = patterns('',
                       url(r'^$', csrf_exempt(search), name='core-index'),
                       url(r'^interface/', include('core.interface.urls')),
                       url(r'^vlan/', include('core.vlan.urls')),
                       url(r'^network/', include('core.network.urls')),
                       url(r'^site/', include('core.site.urls')),
                       url(r'^range/', include('core.range.urls')),
                       url(r'^build/', include('core.build.urls')),
                       url(r'^search/', include('core.search.urls')),
                       url(r'^bulk_change/', include('core.bulk_change.urls')),
                       )
