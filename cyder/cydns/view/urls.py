from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.view.views import *

urlpatterns = patterns('',
   url(r'^$', ViewListView.as_view(), name='view-list'),

   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(ViewCreateView.as_view()), name='view-create-in-domain'),
   url(r'create/$', csrf_exempt(ViewCreateView.as_view()), name='view-create'),

   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(ViewUpdateView.as_view()), name='view-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(ViewDeleteView.as_view()), name='view-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(ViewDetailView.as_view()), name='view-detail'),
)
