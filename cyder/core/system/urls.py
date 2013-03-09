from django.conf.urls.defaults import *

from cyder.core.system.views import *


urlpatterns = patterns('',
    url(r'^$', system_view, name='system'),
    url(r'^(?P<pk>[\w-]+)/update/$', system_view,
        name='system-update'),
    url(r'^(?P<pk>[\w-]+)/delete/$', system_delete,
        name='system-delete'),
    url(r'^(?P<pk>[\w-]+)/tableupdate/$', system_table_update,
        name='system-table-update'),
    url(r'^get/', system_get_update_form, name='system-get-update-form'),
    url(r'^search/', system_search_obj, name='system-search'),

    url(r'^(?P<pk>\d+)$', system_detail, name='system-detail'),
)
