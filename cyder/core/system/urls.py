from django.conf.urls.defaults import *

from cyder.core.ctnr.views import *

urlpatterns = patterns('cyder.core.system.views',
    url(r'^$', 'systems', name='systems'),
)
