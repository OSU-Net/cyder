from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.views import cydns_record_view
from cyder.cydns.address_record.views import *

urlpatterns = patterns('',
    url(r'^$', cydns_record_view, name='address_record'),

    url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(AddressRecordCreateView.as_view()),
       name='address_record-create-in-domain'),

    url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(AddressRecordUpdateView.as_view()),
       name='address_record-update'),
    url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(AddressRecordDeleteView.as_view()),
       name='address_record-delete'),
    url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(AddressRecordDetailView.as_view()),
       name='address_record-detail'),
)
