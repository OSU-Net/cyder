from django.conf.urls.defaults import *

from cyder.core.system.views import system_detail
from cyder.core.urls import core_urls


urlpatterns = core_urls('system') + patterns('',
    url(r'^(?P<pk>\d+)$', system_detail, name='system-detail'),
)
