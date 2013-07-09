from django.db import models

from cyder.base.mixins import ObjectUrlMixin


class View(models.Model, ObjectUrlMixin):
    """
    >>> View(name=name)
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    display_fields = ('name',)

    def details(self):
        return (
            ('Name', self.name),
        )

    def __str__(self):
        return " ".join([getattr(self, f) for f in self.display_fields])

    def __repr__(self):
        return "<View: {0}>".format(self)

    class Meta:
        db_table = 'view'
        unique_together = ('name',)
