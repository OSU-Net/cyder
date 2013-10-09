from cyder.api.v1.endpoints.dhcp.tests import DHCPAPITests
from cyder.cydhcp.site.models import Site


class SiteAPI_Test(DHCPAPITests):
    model = Site

    def create_data(self):
        return self.model.objects.get_or_create(name="site")[0]
