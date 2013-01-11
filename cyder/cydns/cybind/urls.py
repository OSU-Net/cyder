from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cydns.cybind.views import *

urlpatterns = patterns('',
    url(r'^build_debug/(?P<soa_pk>[\w-]+)/$',
        csrf_exempt(build_debug_soa)),
)
