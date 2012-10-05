from django.conf.urls.defaults import *

from cyder.core.network.views import *
from cyder.core.network.network_wizard import *


urlpatterns = patterns('',
                       url(r'^$', NetworkListView.as_view(), name='network-list'),
                       url(r'^wizard_create/$', network_wizard, name='network-wizard'),
                       url(r'^create/$', create_network, name='network-create'),
                       url(r'^(?P<network_pk>[\w-]+)/$', network_detail, name='network-detail'),
                       url(r'^(?P<network_pk>[\w-]+)/update/$',
                           update_network, name='network-update'),
                       url(r'^(?P<pk>[\w-]+)/delete/$',
                           NetworkDeleteView.as_view(), name='network-delete'),
                       url(r'^attr/(?P<attr_pk>[\w-]+)/delete/$',
                           delete_network_attr, name='network-attr'),

                       )
