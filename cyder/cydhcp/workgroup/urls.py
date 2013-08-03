from django.conf.urls.defaults import *

from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.workgroup.views import workgroup_detail

urlpatterns = cydhcp_urls('workgroup') + patterns(
    '',
    url(r'^(?P<pk>[\w-]+)/$', workgroup_detail, name='workgroup-detail'),
)
