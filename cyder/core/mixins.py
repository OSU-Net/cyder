from django.conf import settings
from django.core.urlresolvers import reverse

class ObjectUrlMixin(object):
    """
    This is a mixin that adds important url methods to a model. This
    class uses the ``_meta.db_table`` instance variable of an object to
    calculate URLs. Because of this, you must use the app label of your
    class when declaring urls in your urls.py.
    """
    # TODO. using app_label breaks shit. Go through all the models and
    # assign a better field.  Something like "url handle".  TODO2. Using
    # db_table for now. It looks weird, but it works.
    def get_absolute_url(self):
        """
        Return the absolute url of an object.
        """
        return reverse(self._meta.db_table + '-detail', args=[self.pk])

    def absolute_url(self):
        return self.get_absolute_url()

    def get_edit_url(self):
        """
        Return the edit url of an object.
        """
        return reverse(self._meta.db_table + '-update', args=[self.pk])

    def get_delete_url(self):
        """
        Return the delete url of an object.
        """
        return reverse(self._meta.db_table + '-delete', args=[self.pk])

    def get_create_url(self):
        """
        Return the create url of the type of object.
        """
        try:
            return reverse(self._meta.db_table + '-create', args=[self.pk])
    	except:
		    return reverse(self._meta.db_table + '-create')
