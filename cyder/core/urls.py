from django.conf.urls.defaults import *

from cyder.core.views import (core_index, core_view, core_table_update,
                              core_get_update_form, core_search_obj,
                              core_delete)


def core_urls(object_type):
    """Url generator for Core views"""
    return patterns('',
        url(r'^$', core_view, name=object_type),
        url(r'^(?P<pk>[\w-]+)/update/$', core_view,
            name=object_type + '-update'),
        url(r'^(?P<pk>[\w-]+)/delete/$', core_delete,
            name=object_type + '-delete'),
        url(r'^(?P<pk>[\w-]+)/tableupdate/$', core_table_update,
            name=object_type + '-table-update'),
    )


urlpatterns = patterns('',
    url(r'^$', core_index, name='core-index'),

    url(r'^record/get/', core_get_update_form, name='core-get-update-form'),
    url(r'^record/search/', core_search_obj, name='core-search'),

    url(r'^ctnr/', include('cyder.core.ctnr.urls')),
    url(r'^system/', include('cyder.core.system.urls')),
    url(r'^user/', include('cyder.core.cyuser.urls')),
)
