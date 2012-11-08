from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals

from cyder.core.cyuser import backends
from cyder.core.ctnr.models import Ctnr


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    default_ctnr = models.ForeignKey(Ctnr, default=2)
    phone_number = models.IntegerField(null=True)

    has_perm = backends.has_perm

    class Meta:
        db_table = 'auth_user_profile'


def create_user_profile(sender, **kwargs):
    user = kwargs['instance']

    if (kwargs.get('created', True) and not kwargs.get('raw', False)):
        profile = UserProfile(user=user)
        profile.save()


signals.post_save.connect(create_user_profile, sender=User)
