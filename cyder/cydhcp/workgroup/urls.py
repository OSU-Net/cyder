from cyder.cydhcp.urls import cydhcp_urls
from cyder.cydhcp.workgroup.views import workgroup_detail
from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^(?P<workgroup_pk>[\w-]+)/$',
        workgroup_detail, name='workgroup-detail')
) + cydhcp_urls('workgroup')
