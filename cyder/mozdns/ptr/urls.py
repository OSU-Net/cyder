from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.mozdns.ptr.views import *

urlpatterns = patterns('',
   url(r'^$', csrf_exempt(PTRListView.as_view()), name='ptr-list'),
   url(r'create/$', csrf_exempt(PTRCreateView.as_view()), name='ptr-create'),
   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(PTRUpdateView.as_view()), name='ptr-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(PTRDeleteView.as_view()), name='ptr-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(PTRDetailView.as_view()), name='ptr-detail'),
)
