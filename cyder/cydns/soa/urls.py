from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.soa.views import *
from cyder.cydns.views import cydns_list_create_record

urlpatterns = patterns('',
   url(r'^$', cydns_list_create_record,name='soa-list'),

   url(r'attr/$', delete_soa_attr, name='soa-attr'),

   url(r'(?P<pk>[\w-]+)/update/$',
       cydns_list_create_record, name='soa-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(SOADeleteView.as_view()), name='soa-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(SOADetailView.as_view()), name='soa-detail'),
)
