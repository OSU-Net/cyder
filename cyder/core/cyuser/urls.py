from django.conf.urls.defaults import *
from cyder.core.cyuser.views import clone_perms, delete


urlpatterns = patterns(
    'cyder.core.cyuser.views',
    url(r'search/', 'search', name='user-search'),
    url(r'clone_perms/(?P<user_id>[\w\d-]+)?/$', clone_perms, name='clone_perms'),
    url(r'delete/(?P<user_id>[\w\d-]+)?/$', delete, name='user-delete'),
    url(r'unbecome_user/', 'unbecome_user', name='unbecome-user'),
    url(r'(?P<username>[\w\d-]+)?/?become_user/', 'become_user',
        name='become-user'),
    url(r'(?P<pk>[\w\d-]+)?/$', 'user_detail',
        name='auth_user_profile-detail'),
)
