from cyder.cydns.txt.models import TXT
from cyder.api.v1.tests.base import APITests


class TXTAPI_Test(APITests):
    __test__ = True
    model = TXT

    def create_data(self):
        return TXT.objects.create(
            ctnr=self.ctnr, label='txt', domain=self.domain, txt_data='Things')
