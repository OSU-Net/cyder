from cyder.api.v1.tests.base import APITests, APIKVTestMixin


class DHCPAPITests(APITests, APIKVTestMixin):
    root = 'dhcp'
