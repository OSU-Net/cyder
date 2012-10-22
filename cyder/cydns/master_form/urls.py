from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from cyder.cydns.master_form.views import *
from cyder.cydns.api.v1.api import v1_dns_api


urlpatterns = patterns('',
                       url(r'^ajax_form/', cydns_record_form_ajax, name='ajax-form'),
                       url(r'^ajax_search/', cydns_record_search_ajax, name='ajax-search'),
                       url(r'^$', cydns_record, name='cydns-record'),
                       )
