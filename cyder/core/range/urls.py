from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.core.range.views import *

urlpatterns = patterns('',
    url(r'^$', csrf_exempt(RangeListView.as_view()), name='range-list'),
    url(r'find_range/',
       csrf_exempt(redirect_to_range_from_ip), name='range-find'),
    url(r'create/$', csrf_exempt(
       RangeCreateView.as_view()), name='range-create'),
    url(r'(?P<range_pk>[\w-]+)/update/$',
       csrf_exempt(update_range), name='range-update'),
    url(r'attr/(?P<attr_pk>[\w-]+)/delete/$',
       csrf_exempt(delete_range_attr), name='range-delete-attr'),
    url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(RangeDeleteView.as_view()), name='range-delete'),
    url(r'(?P<range_pk>[\w-]+)/$',
       csrf_exempt(range_detail), name='range-detail'),
)
