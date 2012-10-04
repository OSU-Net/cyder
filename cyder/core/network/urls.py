from django.conf.urls.defaults import *

from cyder.core.network.views import *
from cyder.core.network.network_wizard import *


urlpatterns = patterns('',
                       url(r'^$', NetworkListView.as_view()),
                       url(r'^wizard_create/$', network_wizard),
                       url(r'^create/$', create_network),
                       url(r'^(?P<network_pk>[\w-]+)/$', network_detail),
                       url(r'^(?P<network_pk>[\w-]+)/update/$',
                           update_network),
                       url(r'^(?P<pk>[\w-]+)/delete/$',
                           NetworkDeleteView.as_view()),
                       url(r'^attr/(?P<attr_pk>[\w-]+)/delete/$',
                           delete_network_attr),

                       )
