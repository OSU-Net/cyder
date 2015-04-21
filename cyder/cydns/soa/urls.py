from django.conf.urls.defaults import patterns, url

from cyder.cydns.soa.views import soa_detail
from cyder.cydns.urls import cydns_urls


urlpatterns = cydns_urls('soa')

urlpatterns += patterns(
    '',
    url(r'(?P<pk>[\w-]+)/$', soa_detail, name='soa-detail'),
)
