from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.srv.views import *
from cyder.cydns.views import cydns_record_view

urlpatterns = patterns('',
   url(r'^$', cydns_record_view, name='srv-list'),

   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(SRVCreateView.as_view()), name='srv-create-in-domain'),

   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(SRVUpdateView.as_view()), name='srv-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(SRVDeleteView.as_view()), name='srv-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(SRVDetailView.as_view()), name='srv-detail'),
)
