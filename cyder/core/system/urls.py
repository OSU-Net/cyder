from django.conf.urls.defaults import *

from cyder.core.system.views import *


urlpatterns = patterns('',
    url(r'^$', SystemListView.as_view(), name='system'),
    url(r'^system/create/$', SystemListView.as_view(), name='system-create'),
)
