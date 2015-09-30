from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from search.views import get_zones_json
from search.views import search

from activate import CYDER_REVISION

urlpatterns = patterns(
    '',
    url(r'^get_zones_json', get_zones_json),
    url(r'^help/$', direct_to_template,
        {'template': 'search/search_help.html',
         'extra_context': {'cyder_revision': CYDER_REVISION}},
        name='search-help'),
    url(r'^$', search, name='search'),
)
