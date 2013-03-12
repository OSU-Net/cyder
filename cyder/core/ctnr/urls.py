from django.conf.urls.defaults import *

from cyder.core.ctnr.views import *
from cyder.core.urls import core_urls


urlpatterns = core_urls('ctnr') + patterns('',
    url(r'(?P<pk>[\w-]+)/add_user/$', 'add_user', name='ctnr-add-user'),
    url(r'(?P<pk>[\w-]+)?/?change/$', 'change_ctnr', name='ctnr-change'),
)
