from django.conf.urls.defaults import patterns, include


urlpatterns = patterns('',
    (r'^static/', include('cyder.cydhcp.interface.static_intr.urls')),
    (r'^dynamic/', include('cyder.cydhcp.interface.dynamic_intr.urls')),
)
