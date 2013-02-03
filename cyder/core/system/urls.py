from django.conf.urls.defaults import *

from cyder.core.system.views import *


urlpatterns = patterns('',
    url(r'^$', SystemListView.as_view(), name='system'),
    url(r'^create/$', SystemListView.as_view(), name='system-create'),

    # TODO:
    url(r'^(?P<pk>\d+)$', SystemListView.as_view(), name='system-update'),
    url(r'^(?P<pk>\d+)$', SystemListView.as_view(), name='system-delete'),
    url(r'^(?P<pk>\d+)$', SystemListView.as_view(), name='system-detail'),
)
