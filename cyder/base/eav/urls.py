from django.conf.urls.defaults import patterns, url

from cyder.base.eav.views import search


urlpatterns = patterns(
    '',
    url(r'^search/', search, name='eav-search'))
