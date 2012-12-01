from django.conf.urls.defaults import *

from cyder.cydns.views import cydns_record_view


urlpatterns = patterns('',
   url(r'^$', cydns_record_view, name='ptr'),
)
