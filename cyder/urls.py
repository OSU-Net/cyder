from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views import static

from funfactory.monkeypatches import patch
patch()


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
   url(r'^$', direct_to_template, {'template': 'base/index.html'}, name='system-home'),
   (r'^admin/', include(admin.site.urls)),
   (r'^cydns/', include('cyder.cydns.urls')),
   (r'^cydhcp/', include('cyder.cydhcp.urls')),

   (r'^tasty/', include('cyder.core.systems.urls')),
   (r'^search/', include('cyder.core.search.urls')),

   (r'^login/', include('cyder.core.cyuser.urls')),
   (r'^logout/', include('cyder.core.cyuser.urls')),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
