import django.conf.urls.defaults as defaults

import cydns.cybind.views as views


urlpatterns = defaults.patterns(
    '',
    defaults.url(r'^build_debug/(?P<soa_pk>[\w-]+)/$',
                 views.build_debug_soa),
)
