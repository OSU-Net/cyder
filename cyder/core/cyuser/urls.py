from django.conf.urls.defaults import patterns, url
from cyder.core.cyuser.views import (
    clone_perms, clone_perms_check, delete, set_default_ctnr)


urlpatterns = patterns(
    'cyder.core.cyuser.views',
    url(r'search/', 'search', name='user-search'),
    url(r'clone_perms/(?P<user_id>[\w\d-]+)?/$',
        clone_perms, name='clone-perms'),
    url(r'clone_perms_check/$',
        clone_perms_check, name='clone-perms-check'),
    url(r'setdefaultctnr/', set_default_ctnr, name='set-default-ctnr'),
    url(r'delete/(?P<user_id>[\w\d-]+)?/$', delete, name='user-delete'),
    url(r'unbecome_user/', 'unbecome_user', name='unbecome-user'),
    url(r'(?P<username>[\w\d-]+)?/?become_user/', 'become_user',
        name='become-user'),
    url(r'(?P<pk>[\w\d-]+)?/$', 'user_detail',
        name='auth_user_profile-detail'),
)
