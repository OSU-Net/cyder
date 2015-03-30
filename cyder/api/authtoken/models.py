import hmac
import uuid
from hashlib import sha1

from django.db import models
from rest_framework.authtoken.models import AUTH_USER_MODEL

from cyder.base.mixins import ObjectUrlMixin


class Token(models.Model, ObjectUrlMixin):
    """Because Django REST Framework's Token model defines the user field
    a OneToOneField, we need to create a custom class to replace it that allows
    multiple keys per user.
    """
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(AUTH_USER_MODEL)
    purpose = models.CharField(max_length=100)  # purpose of token
    created = models.DateTimeField(auto_now_add=True)
    can_write = models.BooleanField(default=False)  # allow requests sent with
                                                    # this token
                                                    # to alter data

    class Meta:
        app_label = 'cyder'

    @property
    def pretty_name(self):
        return u"{0}: {1}".format(self.user.username, self.purpose)

    pretty_type = 'API Token'

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
