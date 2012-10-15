from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views import static

from cyder.middleware.restrict_to_remote import allow_anyone

from funfactory.monkeypatches import patch
patch()


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
   # Example:


   # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
   # to INSTALLED_APPS to enable admin documentation:
   # (r'^admin/doc/', include('cyder.django.contrib.admindocs.urls')),

   # Uncomment the next line to enable the admin:
   (r'^admin/', include(admin.site.urls)),
   url(r'^$', 'cyder.systems.views.home', name='system-home'),
   url(r'^en-US/$',
       'cyder.systems.views.home', name='system-home'),
   url(
       r'^misc/$', direct_to_template, {
           'template': 'misc.html'},
   name='misc-list'),
   (r'^a(\d+)/$',
    'cyder.systems.views.system_show_by_asset_tag'),
   (r'^systems/', include('cyder.systems.urls')),
   (r'^en-US/systems/', include('cyder.systems.urls')),
   (r'^reports/', include('cyder.reports.urls')),
   (r'^dhcp/', include('cyder.dhcp.urls')),
   (r'^truth/', include('cyder.truth.urls')),
   (r'^user_systems/', include('cyder.user_systems.urls')),
   (r'^build/', include('cyder.build.urls')),
   (r'^tasty/', include('cyder.api_v3.urls')),
   (r'^en-US/tasty/', include('cyder.api_v3.urls')),
   (r'^api/', include('cyder.api_v1.urls')),
   (r'^api/v1/', include('cyder.api_v1.urls')),
   (r'^api/v2/', include('cyder.api_v2.urls')),
   (r'^tokenapi/', include('cyder.api_v2.urls')),

   (r'^en-US/mozdns/', include('cyder.mozdns.urls')),
   (r'^mozdns/', include('cyder.mozdns.urls')),
   (r'^en-US/core/', include('cyder.core.urls')),
   (r'^core/', include('cyder.core.urls')),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
