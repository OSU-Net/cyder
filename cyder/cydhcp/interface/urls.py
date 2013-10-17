from django.conf.urls.defaults import patterns, url

from cyder.cydhcp.interface.views import interface_delete

urlpatterns = patterns(
    '',
    url(r'^interface_delete/', interface_delete, name='interface-delete'),
)
