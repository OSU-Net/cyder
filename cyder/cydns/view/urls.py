from django.conf.urls.defaults import *

from cyder.cydns.view.views import *


urlpatterns = patterns(
    '',

    url(r'^$', ViewListView.as_view(), name='view-list'),

    url(r'(?P<domain>[\w-]+)/create/$',
        ViewCreateView.as_view(), name='view-create-in-domain'),
    url(r'create/$', ViewCreateView.as_view(), name='view-create'),

    url(r'(?P<pk>[\w-]+)/update/$',
        ViewUpdateView.as_view(), name='view-update'),
    url(r'(?P<pk>[\w-]+)/delete/$',
        ViewDeleteView.as_view(), name='view-delete'),
    url(r'(?P<pk>[\w-]+)/$',
        ViewDetailView.as_view(), name='view-detail'),
)
