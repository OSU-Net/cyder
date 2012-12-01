from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views import static

from funfactory.monkeypatches import patch
patch()

from cyder.core.cyuser import views as cyuser_views


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
   (r'^$', include('cyder.core.system.urls')),

   (r'^admin/', include(admin.site.urls)),
   (r'^cydns/', include('cyder.cydns.urls')),
   (r'^cydhcp/', include('cyder.cydhcp.urls')),

   (r'^ctnr/', include('cyder.core.ctnr.urls')),
   (r'^search/', include('cyder.core.search.urls')),

   url(r'^login/$', cyuser_views.cylogin, name='login'),
   url(r'^logout/$', cyuser_views.cylogout, name='logout'),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
