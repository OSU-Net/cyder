from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_detail, object_list

from misc.generic_views import create_object, update_object, delete_object, gen_mod_dict, gen_info_dict, gen_del_dict

urlpatterns = patterns('cyder.dhcp',
   url(r'^show/$', 'views.showall', name='dhcp-list'),
   url(r'^showfile/(.*)[/]$',
       'views.showfile', name='dhcp-show-file'),
   url(r'^override/(.*)[/]$', 'views.override_file',
       name='dhcp-show-override'),
   url(r'^new/$', 'views.new', name='dhcp-new'),
   # TODO this shit is fucked up.  views.create is a bullshit view
   # figure this out later
   url(r'^edit/(.*)[/]$', 'views.edit', name='dhcp-update'),
   url(r'^edit/$', 'views.create', name='dhcp-create'),
   url(r'^delete/(.*)/$', 'views.delete', name='dhcp-delete'),
)
