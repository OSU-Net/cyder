from django.conf.urls.defaults import include, patterns, url

from cyder.core.views import (core_index, core_view, core_table_update,
                              core_search_obj)
from cyder.base.views import static_dynamic_view


def core_urls(object_type):
    """Url generator for Core views"""
    return patterns(
        '',
        url(r'^$', core_view, name=object_type),
        url(r'^(?P<pk>[\w-]+)/update/$', core_view,
            name=object_type + '-update'),
        url(r'^(?P<pk>[\w-]+)/tableupdate/$', core_table_update,
            name=object_type + '-table-update'),
    )


urlpatterns = patterns(
    '',
    url(r'^$', core_index, name='core-index'),

    url(r'^record/search/', core_search_obj, name='core-search'),

    url(r'^ctnr/', include('cyder.core.ctnr.urls')),
    url(r'^system/', include('cyder.core.system.urls')),
    url(r'^user/', include('cyder.core.cyuser.urls')),

    url(r'^interfaces/$', static_dynamic_view, name='interfaces'),
)

urlpatterns += patterns(
    '',
    url(r'^system_av/', include(core_urls('system_av')))
)
