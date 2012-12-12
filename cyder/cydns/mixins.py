from django.conf import settings
from django.core.urlresolvers import reverse


class ObjectUrlMixin(object):
    """
    This is a mixin that adds important url methods to a model. This
    class uses the ``_meta.db_table`` instance variable of an object to
    calculate URLs. Because of this, you must use the app label of your
    class when declaring urls in your urls.py.
    """
    @classmethod
    def get_list_url(cls):
        """
        Return the 'list' url of an object.
        """
        return reverse(cls._meta.db_table)

    @classmethod
    def get_create_url(cls):
        """
        Return the create url of the type of object (to be posted to).
        """
        return cls.get_list_url() + '?action=create'

    def get_update_url(self):
        """
        Return the update url of an object (to be posted to).
        """
        return self.get_list_url() + '?action=update&pk=' + str(self.pk)

    def get_delete_url(self):
        """
        Return the delete url of an object (to be posted to).
        """
        return self.get_list_url() + '?action=delete&pk=' + str(self.pk)

    def get_detail_url(self):
        """
        Return the detail url of an object.
        """
        return reverse(self._meta.db_table + '-detail', args=[self.pk])
