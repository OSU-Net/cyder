from django.conf.urls.defaults import url, patterns

from cyder.core.system.views import system_create_view, system_detail
from cyder.core.urls import core_urls


urlpatterns = core_urls('system') + patterns(
    '',
    url(r'^(?P<pk>\d+)$', system_detail, name='system-detail'),
    url(r'^create/(?P<initial>[\w-]+)', system_create_view,
        name='system-create'),
)
