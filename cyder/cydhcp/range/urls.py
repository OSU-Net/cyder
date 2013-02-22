from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydhcp.range.views import *
from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = patterns('',
    url(r'find_range/',
       csrf_exempt(redirect_to_range_from_ip), name='range-find'),
    url(r'(?P<range_pk>[\w-]+)/$',
       csrf_exempt(range_detail), name='range-detail'),
) + cydhcp_urls('range')
