from django.conf.urls.defaults import url, patterns
from cyder.cydhcp.vlan.views import vlan_detail
from cyder.cydhcp.urls import cydhcp_urls


urlpatterns = cydhcp_urls('vlan') + patterns('',
    url(r'^(?P<vlan_pk>[\w-]+)/$', vlan_detail,
        name='vlan-detail'),
)
