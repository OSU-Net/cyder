from django.conf.urls.defaults import *

from cyder.core.ctnr.views import *
from cyder.core.urls import core_urls


urlpatterns = core_urls('ctnr') + patterns(
    '',
    url(r'(?P<pk>[\w-]+)/add_user/$', add_user, name='ctnr-add-user'),
    url(r'(?P<ctnr_pk>[\w-]+)/remove_user/(?P<user_pk>[\w-]+)/$', remove_user,
        name='ctnr-remove-user'),
    url(r'(?P<ctnr_pk>[\w-]+)/update_user_level/(?P<user_pk>[\w-]+)/'
        '(?P<lvl>[\w-]+)/$',
        update_user_level, name='update-user-level'),
    url(r'(?P<pk>[\w-]+)?/?change/$', change_ctnr, name='ctnr-change'),
    url(r'(?P<pk>[\w-]+)/$', CtnrDetailView.as_view(), name='ctnr-detail'),
)
