from cyder.cydns.mx.models import MX
from cyder.api.v1.tests.base import APITests


class MXAPI_Test(APITests):
    __test__ = True
    model = MX

    def create_data(self):
        return MX.objects.create(
            ctnr=self.ctnr, description='MX Record', label='mail',
            domain=self.domain, server='relay.oregonstate.edu', ttl=420,
            priority=420)
