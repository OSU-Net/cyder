from django.conf.urls.defaults import *

urlpatterns = patterns(
    'cyder.api.authtoken.views',
    url(r'request/', 'request_token', name='request-token'),
    url(r'revoke/(?P<pk>[\w\d-]+)?/$', 'revoke_token'),
    url(r'(?P<pk>[\w\d-]+)?/$', 'token_detail',
        name='authtoken_token-detail'),
)
