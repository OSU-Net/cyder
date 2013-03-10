from django.conf.urls.defaults import *

from cyder.cydhcp.build.views import *

urlpatterns = patterns('',
    url(r'(?P<network_pk>[\w-]+)/$', build_network, name='build-network'),
)
