from django.conf.urls.defaults import patterns, url

from cyder.cydns.soa.views import delete_soa_attr, soa_detail
from cyder.cydns.urls import cydns_urls


urlpatterns = cydns_urls('soa')

urlpatterns += patterns(
    '',
    url(r'attr/$', delete_soa_attr, name='soa-attr'),
    url(r'(?P<pk>[\w-]+)/$', soa_detail,
    name='soa-detail'),
)
