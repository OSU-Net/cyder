from django.conf.urls.defaults import *


urlpatterns = patterns('cyder.core.cyuser.views',
    url(r'search/', 'search', name='user-search'),
    url(r'unbecome_user/', 'unbecome_user', name='unbecome-user'),
    url(r'(?P<username>[\w\d-]+)?/?become_user/', 'become_user',
        name='become-user'),
)
