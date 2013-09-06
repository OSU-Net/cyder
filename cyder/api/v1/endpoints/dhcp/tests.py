from cyder.api.v1.tests.base import APITests, APIKVTestMixin


class DHCPAPITests(APITests, APIKVTestMixin):
    root = 'dhcp'

    def __init__(self, *args, **kwargs):
        super(DHCPAPITests, self).__init__(self, *args, **kwargs)
        super(APITests, self).__init__(self, *args, **kwargs)
