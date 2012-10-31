from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.views import cydns_list_create_view
from cyder.cydns.address_record.views import *

urlpatterns = patterns('',
    url(r'^$', cydns_list_create_view, name='address-record-list',
        kwargs={'record_type': 'Address Record'}),
    url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(AddressRecordCreateView.as_view()),
       name='address-record-create-in-domain'),
    url(r'create/', csrf_exempt(
       AddressRecordCreateView.as_view()), name='address-record-create'),
    url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(AddressRecordUpdateView.as_view()),
       name='address-record-update'),
    url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(AddressRecordDeleteView.as_view()),
       name='address-record-delete'),
    url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(AddressRecordDetailView.as_view()),
       name='address-record-detail'),
)
