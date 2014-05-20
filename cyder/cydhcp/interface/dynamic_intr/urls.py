from django.conf.urls.defaults import patterns, url
from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.interface.dynamic_intr.views import dynamic_intr_detail

urlpatterns = cydhcp_urls('dynamic_interface') + patterns(
    '',
    url(r'(?P<pk>[\w-]+)/$', dynamic_intr_detail,
        name='dynamic_interface-detail'),)
