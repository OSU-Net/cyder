from django.conf.urls.defaults import patterns, url
from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.interface.static_intr.views import static_intr_detail

urlpatterns = cydhcp_urls('static_interface') + patterns(
    '',
    url(r'(?P<pk>[\w-]+)/$', static_intr_detail,
        name='static_interface-detail'),)
