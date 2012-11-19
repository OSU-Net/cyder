from django.conf import settings
from django.core.urlresolvers import reverse


class ObjectUrlMixin(object):
    """
    This is a mixin that adds important url methods to a model. This
    class uses the ``_meta.db_table`` instance variable of an object to
    calculate URLs. Because of this, you must use the app label of your
    class when declaring urls in your urls.py.
    """
    def get_detail_url(self):
        """
        Return the detail url of an object.
        """
        return reverse(self._meta.db_table.replace('-', '_') + '-detail',
                       args=[self.pk])

    def get_list_url(self):
        """
        Return the list url of an object.
        """
        return reverse(self._meta.db_table.replace('-', '_') + '-list')

    def get_update_url(self):
        """
        Return the update url of an object.
        """
        return reverse(self._meta.db_table.replace('-', '_') + '-update',
                       args=[self.pk])

    def get_delete_url(self):
        """
        Return the delete url of an object.
        """
        return reverse(self._meta.db_table.replace('-', '_') + '-delete',
                       args=[self.pk])

    def get_create_url(self):
        """
        Return the create url of the type of object.
        """
        try:
            return reverse(self._meta.db_table.replace('-', '_') + '-create',
                           args=[self.pk])
        except:
            return reverse(self._meta.db_table.replace('-', '_') + '-create')
