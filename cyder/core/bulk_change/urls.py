from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.core.bulk_change.views import *

urlpatterns = patterns('',
    url(r'^bulk_change_ajax',
        csrf_exempt(bulk_change_ajax), name='bulk-change-ajax'),
    url(r'^$', csrf_exempt(bulk_change), name='bulk-change'),
)
