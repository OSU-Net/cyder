from cyder.cydhcp.site.models import Site
from cyder.api.v1.tests.base import APITests


class SiteAPI_Test(APITests):
    __test__ = True
    model = Site

    def create_data(self):
        return self.model.objects.get_or_create(name="site")[0]
