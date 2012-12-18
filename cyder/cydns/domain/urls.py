from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.urls import cydns_urls
from cyder.cydns.domain.views import *


urlpatterns = cydns_urls('domain')


urlpatterns += patterns('',
    url(r'^get_all_domains/$', get_all_domains, name='get-all-domains'),
    url(r'create/$', csrf_exempt(DomainCreateView.as_view()),
        name='domain-create'),
    url(r'(?P<pk>[\w-]+)/$', csrf_exempt(DomainDetailView.as_view()),
        name='domain-detail'),
)
