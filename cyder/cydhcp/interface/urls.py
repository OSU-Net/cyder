from django.conf.urls.defaults import *


urlpatterns = patterns('cyder.cydhcp.interface.static_intr.views',
   url(r'^create/$', 'create_no_system_static_interface',
       name='static_interface-create'),
   url(r'^(?P<system_pk>[\w-]+)/create/$', 'create_static_interface',
       name='static_interface-create-system'),
   url(r'^(?P<system_pk>[\w-]+)/quick_create/$', 'quick_create',
       name='static_interface-create-quick'),

   url(r'^(?P<intr_pk>[\w-]+)/$', 'detail_static_interface',
       name='static_interface-detail'),
   url(r'^(?P<intr_pk>[\w-]+)/update/$', 'edit_static_interface',
       name='static_interface-update'),
   url(r'^(?P<intr_pk>[\w-]+)/delete/$', 'delete_static_interface',
       name='static_interface-delete'),

   url(r'^attr/(?P<attr_pk>[\w-]+)/delete/$', 'delete_attr',
       name='attr-delete'),
   url(r'^combine_a_ptr_to_interface/(?P<addr_pk>[\w-]+)/(?P<ptr_pk>[\w-]+)/$',
       'combine_a_ptr_to_interface', name='the_longest_damn_url_in_the_world')
)
