import django.conf.urls.defaults as defaults
from django.views.decorators.csrf import csrf_exempt

import cydns.cybind.views as views

urlpatterns = defaults.patterns(
    '',
    defaults.url(r'^build_debug/(?P<soa_pk>[\w-]+)/$',
    csrf_exempt(views.build_debug_soa)),
)
