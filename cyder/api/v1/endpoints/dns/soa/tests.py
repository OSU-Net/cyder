from cyder.api.v1.tests.base import APIEAVTestMixin, build_domain, APITests
from cyder.cydns.soa.models import SOA


class SOAAPI_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = SOA

    def create_data(self):
        return SOA.objects.create(
            primary='ns1.oregonstate.edu', contact='admin.oregonstate.edu',
            retry=420, refresh=420, description='Test SOA',
            root_domain=build_domain("soaapi_test", self.domain))
