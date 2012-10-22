from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.address_record.views import *

urlpatterns = patterns('',
    url(r'^$', csrf_exempt(
       AddressRecordListView.as_view()), name='address-record-list'),
    url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(AddressRecordCreateView.as_view()),
       name='address-record-create-by-domain'),
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
