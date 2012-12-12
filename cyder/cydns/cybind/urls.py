from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.cybind.views import *

urlpatterns = patterns('',
   url(r'^build_debug/(?P<soa_pk>[\w-]+)/$',
       csrf_exempt(build_debug_soa), name='build-debug'),
   url(r'^build/(?P<soa_pk>[\w-]+)/$',
       csrf_exempt(build_soa), name='buid-soa'),
)
