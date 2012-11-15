from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.mx.views import *
from cyder.cydns.views import cydns_record_view


urlpatterns = patterns('',
   url(r'^$', cydns_record_view, name='mx'),

   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(MXCreateView.as_view()), name='mx-create-in-domain'),

   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(MXUpdateView.as_view()), name='mx-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(MXDeleteView.as_view()), name='mx-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(MXDetailView.as_view()), name='mx-detail'),
)
