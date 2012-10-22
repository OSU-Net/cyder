from django.conf.urls.defaults import *

from tastytools.api import Api

from .system_api import (SystemResource, ServerModelResource,
                         OperatingSystemResource, KeyValueResource,
                         AllocationResource, LocationResource,
                         SystemRackResource, SystemStatusResource,
                         OperatingSystemData)

system_api = Api(api_name='systems')
system_api.register(SystemResource())
system_api.register(ServerModelResource())
system_api.register(OperatingSystemResource())
system_api.register(KeyValueResource())
system_api.register(AllocationResource())
system_api.register(LocationResource())
system_api.register(SystemRackResource())
system_api.register(SystemStatusResource())
system_api.register_testdata(OperatingSystemData)
urlpatterns = patterns('',
    (r'', include(system_api.urls)),
    (r'^tastytools/', include('tastytools.urls'), {'api_name':
        system_api.api_name}),
)
