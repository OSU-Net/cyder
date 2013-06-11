from django.conf.urls.defaults import *

from cyder.cydns.soa.views import *
from cyder.cydns.urls import cydns_urls


urlpatterns = cydns_urls('soa')

urlpatterns += patterns('',
                        url(r'attr/$', delete_soa_attr, name='soa-attr'),
                        url(r'(?P<pk>[\w-]+)/$', SOADetailView.as_view(),
                            name='soa-detail'),
)
