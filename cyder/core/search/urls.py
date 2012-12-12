from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template

from cyder.core.search.views import *

urlpatterns = patterns('',
    url(r'^$', csrf_exempt(search),name='search'),
    url(r'^help/$', direct_to_template, {'template': 'search/search_help.html'}, name='search-help'),
)
