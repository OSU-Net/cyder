from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.ptr.views import *
from cyder.cydns.views import cydns_list_create_record

urlpatterns = patterns('',
   url(r'^$', cydns_list_create_record, name='ptr-list',
       kwargs={'record_type': 'ptr'}),

   url(r'(?P<pk>[\w-]+)/update/$',
       cydns_list_create_record, name='ptr-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(PTRDeleteView.as_view()), name='ptr-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(PTRDetailView.as_view()), name='ptr-detail'),
)
