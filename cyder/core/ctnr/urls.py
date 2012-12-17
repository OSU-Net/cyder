from django.conf.urls.defaults import *

from cyder.core.ctnr.views import *


urlpatterns = patterns('cyder.core.ctnr.views',
    url(r'^$', CtnrListView.as_view(), name='ctnr-list'),
    url(r'create/$', CtnrCreateView.as_view(), name='ctnr-create'),
    url(r'(?P<pk>[\w-]+)/update/$', CtnrUpdateView.as_view(),
        name='ctnr-update'),
    url(r'(?P<pk>[\w-]+)/delete/$', CtnrDeleteView.as_view(),
        name='ctnr-delete'),
    url(r'(?P<pk>[\w-]+)/add_user/$', 'add_user', name='ctnr-add-user'),
    url(r'(?P<pk>[\w-]+)?/?change/$', 'change_ctnr', name='ctnr-change'),
    url(r'(?P<pk>[\w-]+)/$', CtnrDetailView.as_view(), name='ctnr-detail'),
)
