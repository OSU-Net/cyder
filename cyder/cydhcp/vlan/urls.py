from django.conf.urls.defaults import *

from cyder.cydhcp.vlan.views import *

urlpatterns = patterns('',
   url(r'^$', VlanListView.as_view(), name='vlan-list'),
   url(r'^create/$', VlanCreateView.as_view(), name='vlan-create'),
   url(r'^(?P<vlan_pk>[\w-]+)/$', vlan_detail, name='vlan-detail'),
   url(r'^(?P<vlan_pk>[\w-]+)/update/$', update_vlan, name='vlan-update'),
   url(r'^(?P<pk>[\w-]+)/delete/$',
       VlanDeleteView.as_view(), name='vlan-delete'),
)
