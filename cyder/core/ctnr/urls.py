from django.conf.urls.defaults import patterns, url

from cyder.core.ctnr.views import (add_object, remove_object, remove_user,
                                   update_user_level, change_ctnr,
                                   ctnr_detail)
from cyder.core.urls import core_urls


urlpatterns = core_urls('ctnr') + patterns(
    '',
    url(r'(?P<ctnr_pk>[\w-]+)/add_object/$', add_object,
        name='ctnr-add-object'),
    url(r'(?P<ctnr_pk>[\w-]+)/remove_object/(?P<obj_type>[\w-]+)/'
    '(?P<obj_pk>[\w-]+)/', remove_object, name='ctnr-remove-object'),
    url(r'(?P<ctnr_pk>[\w-]+)/remove_user/(?P<user_pk>[\w-]+)/$', remove_user,
        name='ctnr-remove-user'),
    url(r'(?P<ctnr_pk>[\w-]+)/update_user_level/(?P<user_pk>[\w-]+)/'
        '(?P<lvl>[\w-]+)/$',
        update_user_level, name='update-user-level'),
    url(r'(?P<pk>[\w-]+)?/?change/$', change_ctnr, name='ctnr-change'),
    url(r'(?P<pk>[\w-]+)/$', ctnr_detail, name='ctnr-detail'),
)
