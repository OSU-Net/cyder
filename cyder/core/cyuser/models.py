from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals

from cyder.base.mixins import ObjectUrlMixin
from cyder.core.cyuser import backends
from cyder.core.ctnr.models import Ctnr


class UserProfile(models.Model, ObjectUrlMixin):
    user = models.OneToOneField(User, related_name='profile')
    default_ctnr = models.ForeignKey(Ctnr, default=2)
    phone_number = models.IntegerField(null=True)

    has_perm = backends.has_perm
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    class Meta:
        db_table = 'auth_user_profile'

    def __str__(self):
        return self.user.username

    def details(self):
        """For tables."""
        data = super(UserProfile, self).details()
        data['data'] = [
            ('Username', 'user__username', self),
            ('First Name', 'user__firstname', self.user.first_name),
            ('Last Name', 'user__lastname', self.user.last_name),
            ('Email', 'user__email', self.user.email),
        ]
        return data

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                p = UserProfile.objects.get(user=self.user)
                self.pk = p.pk
            except UserProfile.DoesNotExist:
                pass
        super(UserProfile, self).save(*args, **kwargs)

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        if objects:
            return UserProfile.objects.filter(pk__in=
                ctnr.users.filter(pk__in=objects)
                .values_list('profile', flat=True))
        else:
            return UserProfile.objects.filter(pk__in=
                ctnr.users.all().values_list('profile', flat=True))


def create_user_profile(sender, **kwargs):
    user = kwargs['instance']

    if (kwargs.get('created', True) and not kwargs.get('raw', False)):
        profile = UserProfile(user=user)
        profile.save()


signals.post_save.connect(create_user_profile, sender=User)
