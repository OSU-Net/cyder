from django.conf.urls.defaults import *

from cyder.cydns.urls import cydns_urls
from cyder.cydns.domain.views import *


urlpatterns = cydns_urls('domain')


urlpatterns += patterns('',
    url(r'^get_all_domains/$', get_all_domains, name='get-all-domains'),
    url(r'create/$', DomainCreateView.as_view(),
        name='domain-create'),
    url(r'(?P<pk>[\w-]+)/$', DomainDetailView.as_view(),
        name='domain-detail'),
)
