import json

from django.test.client import Client, FakePayload
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

class CyderAPITestClient(object):
    """Custom test case class to facilitate easier testing.
    Only supports glorious JSON master race.
    """

    def __init__(self, serializer=None):
        self.client = Client()

        if not serializer:
            self.serializer = serializers.Serializer()
        else:
            self.serializer = serializer

    def get(self, uri, data=None, authentication=None, **kwargs):
        if 'HTTP_ACCEPT' not in kwargs:
            kwargs['HTTP_ACCEPT'] = 'application/json'

        if data is not None:
            kwargs['data'] = data

        if authentication is not None:
            kwargs['HTTP_AUTHORIZATION'] = authentication

        return self.client.get(uri, **kwargs)

    def post(self, uri, data=None, authentication=None, **kwargs):
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'application/json'

        if data is not None:
            kwargs['data'] = data.data

        if authentication is not None:
            kwargs['HTTP_AUTHORIZATION'] = authentication

        return self.client.post(uri, **kwargs)

    def put(self, uri, data=None, authentication=None, **kwargs):
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'application/json'

        if data is not None:
            kwargs['data'] = data.data

        if authentication is not None:
            kwargs['HTTP_AUTHORIZATION'] = authentication

        return self.client.put(uri, **kwargs)

    def patch(self, uri, data=None, authentication=None, **kwargs):
        if 'content_type' not in kwargs:
            content_type = kwargs['content_type'] = 'application/json'
        else:
            content_type = kwargs['content_type']

        if authentication is not None:
            kwargs['HTTP_AUTHORIZATION'] = authentication

        parsed = urlparse(uri)
        r = {
                'CONTENT_LENGTH': len(kwargs['data']),
                'CONTENT_TYPE': content_type,
                'PATH_INFO': self.client._get_path(parsed),
                'QUERY_STRING': parsed[4],
                'REQUEST_METHOD': 'PATCH',
                'wsgi.input': FakePayload(kwargs['data']),
        }
        r.update(kwargs)

        return self.client.request(**r)

    def delete(self, uri, data=None, authentication=None, **kwargs):
        if 'content_type' not in kwargs:
            kwargs['content_Type'] = 'application/json'

        if data is not None:
            kwargs['data'] = data

        if authentication is not None:
            kwargs['HTTP_AUTHORIZATION'] = authentication

        return self.client.delete(uri, **kwargs)

class HttpAssertsMixin(object):
    def assertHttpOK(self, resp):
        assert resp.status_code == 200

    def assertHttpCreated(self, resp):
        assert resp.status_code == 201

    def assertHttpAccepted(self, resp):
        assert resp.status_code in (202, 204)

    def assertHttpBadRequest(self, resp):
        assert resp.status_code == 400

    def assertHttpUnauthorized(self, resp):
        assert resp.status_code == 401

    def assertHttpForbidden(self, resp):
        assert resp.status_code == 403

    def assertHttpNotFound(self, resp):
        assert resp.status_code == 404

    def assertHttpMethodNotAllowed(self, resp):
        assert resp.status_code == 405

    def assertHttpTooManyRequests(self, resp):
        assert resp.status_code == 429

    def assertHttpApplicationError(self, resp):
        assert resp.status_code == 500

    def assertHttpNotImplemented(self, resp):
        assert resp.status_code == 501

    def assertValidJSON(self, data):
        json.loads(data) # if this fails then the test fails


