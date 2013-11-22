from django.db import models
from django.utils.safestring import mark_safe

from cyder.base.utils import classproperty


class BaseModel(models.Model):
    """
    Base class for models to abstract some common features.

    * Adds automatic created and modified fields to the model.
    """
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        get_latest_by = 'created'

    @classproperty
    @classmethod
    def pretty_type(cls):
        return cls.__name__.lower()

    @property
    def pretty_name(self):
        return unicode(self)

    def unique_error_message(self, model_class, unique_check):
        error = super(BaseModel, self).unique_error_message(
            model_class, unique_check)
        kwargs = {}
        for field in unique_check:
            kwargs[field] = getattr(self, field)

        obj = model_class.objects.filter(**kwargs)
        if obj and hasattr(obj.get(), 'get_detail_url'):
            error = error[:-1] + ' at <a href={0}>{1}.</a>'.format(
                obj.get().get_detail_url(), obj.get())
            error = mark_safe(error)
        return error
