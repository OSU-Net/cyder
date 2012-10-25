from django.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('cyder.core.cyuser.views',
    # url(r'^$', CyuserListView.as_view()),
    url(r'unbecome_user/', 'unbecome_user'),
    url(r'(?P<username>[\w\d-]+)?/?become_user/', 'become_user'),
)
