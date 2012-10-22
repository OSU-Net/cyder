from django.conf.urls.defaults import *

from cyder.core.ctnr.views import *

urlpatterns = patterns('cyder.core.ctnr.views',
    url(r'^$', CtnrListView.as_view()),
    url(r'create/$', CtnrCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', CtnrUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', CtnrDeleteView.as_view()),
    url(r'(?P<pk>[\w-]+)/add_user/$', CtnrUserCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)?/?change/$', 'change_ctnr'),
    url(r'(?P<pk>[\w-]+)/$', CtnrDetailView.as_view()),
)
