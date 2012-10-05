from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.mozdns.mx.views import *


urlpatterns = patterns('',
                       url(r'^$', MXListView.as_view(), name='mx-list'),
                       url(r'(?P<domain>[\w-]+)/create/$',
                           csrf_exempt(MXCreateView.as_view()), name='mx-create-by-domain'),
                       url(r'create/$', csrf_exempt(MXCreateView.as_view()), name='mx-create'),
                       url(r'(?P<pk>[\w-]+)/update/$',
                           csrf_exempt(MXUpdateView.as_view()), name='mx-update'),
                       url(r'(?P<pk>[\w-]+)/delete/$',
                           csrf_exempt(MXDeleteView.as_view()), name='mx-delete'),
                       url(r'(?P<pk>[\w-]+)/$',
                           csrf_exempt(MXDetailView.as_view()), name='mx-detail'),
                       )
