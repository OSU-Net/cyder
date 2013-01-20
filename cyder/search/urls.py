from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from search.views import search_ajax, search_dns_text, get_zones_json
from search.views import search

urlpatterns = patterns('',
    url(r'^search_ajax', search_ajax),
    url(r'^search_dns_text', search_dns_text),
    url(r'^get_zones_json', get_zones_json),
    url(r'^help/$', direct_to_template, {'template':
'search/search_help.html'}, name='search-help'),
    url(r'^$', search, name='search'),
)
