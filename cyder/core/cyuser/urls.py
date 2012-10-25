from django.conf import settings
from django.conf.urls.defaults import *

from cyder.core.cyuser.views import *

urlpatterns = patterns('cyder.core.cyuser.views',
    url(r'login', 'login', name='login'),
    url(r'logout', 'logout', name='logout'),

    # url(r'^$', CyuserListView.as_view()),
    url(r'unbecome_user/', 'unbecome_user'),
    url(r'(?P<username>[\w\d-]+)?/?become_user/', 'become_user'),
)
