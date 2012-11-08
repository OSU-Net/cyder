from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.sshfp.views import *

urlpatterns = patterns('',
   url(r'^$', SSHFPListView.as_view(), name='sshfp-list'),

   url(r'(?P<domain>[\w-]+)/create/$', csrf_exempt(
       SSHFPCreateView.as_view()), name='sshfp-create-in-domain'),
   url(r'create/$', csrf_exempt(
       SSHFPCreateView.as_view()), name='sshfp-create'),

   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(SSHFPUpdateView.as_view()), name='sshfp-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(SSHFPDeleteView.as_view()), name='sshfp-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(SSHFPDetailView.as_view()), name='sshfp-detail'),
)
