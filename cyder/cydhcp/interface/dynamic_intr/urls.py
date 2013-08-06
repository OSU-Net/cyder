from django.conf.urls.defaults import patterns, url
from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.views import cydhcp_create
from cyder.cydhcp.interface.dynamic_intr.views import dynamic_intr_detail

urlpatterns = cydhcp_urls('dynamic_interface') + patterns(
    '',
    url(r'create/$', cydhcp_create, name='dynamic_interface-create'),
    url(r'(?P<pk>[\w-]+)/$', dynamic_intr_detail,
        name='dynamic_interface-detail'),)
