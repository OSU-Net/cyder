from django.conf.urls.defaults import include, patterns, url
from django.conf import settings
from django.contrib import admin

from funfactory.monkeypatches import patch
patch()
from cyder.api.v1.routes import router

from cyder.core.views import core_index
from cyder.base.views import send_email, admin_page

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', core_index, name='core-index'),
    url(r'^api/authtoken/', include('cyder.api.authtoken.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^admin/',  include(admin.site.urls)),
    url(r'^core/',   include('cyder.core.urls')),
    url(r'^dhcp/',   include('cyder.cydhcp.urls')),
    url(r'^dns/',    include('cyder.cydns.urls')),
    url(r'^eav/',    include('cyder.base.eav.urls')),
    url(r'^api/api', include('rest_framework.urls',
        namespace='rest_framework')),
    url(r'^search/', include('cyder.search.urls')),
    url(r'^bug/$', send_email, name='bug-report'),
    url(r'^administration/$', admin_page, name='admin-page'),

    url(r'^accounts/login/$',  'django_cas.views.login',  name='login'),
    url(r'^accounts/logout/$', 'django_cas.views.logout', name='logout'),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns(
        '',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
