from django.conf.urls.defaults import url, patterns
from cyder.cydhcp.vlan.views import VlanCreateView, vlan_detail
from cyder.cydhcp.urls import cydhcp_urls


urlpatterns = patterns('',
                       url(r'^create/$', VlanCreateView.as_view(),
                           name='vlan-create'),
                       url(r'^(?P<vlan_pk>[\w-]+)/$', vlan_detail,
                           name='vlan-detail'),)

urlpatterns += cydhcp_urls('vlan')
