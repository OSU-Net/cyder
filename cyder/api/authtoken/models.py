import hmac
import uuid
from hashlib import sha1

from django.conf import settings
from django.db import models
from rest_framework.compat import AUTH_USER_MODEL

from cyder.base.mixins import ObjectUrlMixin


class Token(models.Model, ObjectUrlMixin):
    """Because Django REST Framework's Token model defines the user field
    a OneToOneField, we need to create a custom class to replace it that allows
    multiple keys per user.
    """
    key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(AUTH_USER_MODEL)
    purpose = models.CharField(max_length=100) # purpose of token
    created = models.DateTimeField(auto_now_add=True)

    """
    class Meta:
        abstract = 'api.authtoken' not in settings.INSTALLED_APPS
    """

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        unique = uuid.uuid4()
        return hmac.new(unique.bytes, digestmod=sha1).hexdigest()

    def __unicode__(self):
        return self.key

    def details(self):
        """For automatic table generation via the tablefy() function."""
        data = super(Token, self).details()
        data['data'] = [
            ('Key', 'token__key', self),
            ('Purpose', 'token__purpose', self.purpose),
            ('Created', 'token__created', self.created),
        ]
        return data
