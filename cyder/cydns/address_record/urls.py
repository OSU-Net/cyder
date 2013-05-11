from django.conf.urls.defaults import *

from cyder.cydns.urls import cydns_urls
from cyder.cydns.address_record.views import address_record_detail


urlpatterns = cydns_urls('address_record') + \
    [url(r'(?P<pk>[\w-]+)/$',
         address_record_detail, name='address_record-detail')]
