from django.conf.urls.defaults import patterns, url

from cyder.cydhcp.interface.views import is_last_interface

urlpatterns = patterns(
    '',
    url(r'^last_interface/', is_last_interface, name='is_last_interface'),
)
