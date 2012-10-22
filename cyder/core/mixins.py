class ObjectUrlMixin(object):
    """
    This is a mixin that adds important url methods to a model. This
    class uses the ``_meta.db_table`` instance variable of an object to
    calculate URLs. Because of this, you must use the app label of your
    class when declaring urls in your urls.py.
    """
    def get_absolute_url(self):
        """
        Return the absolute url of an object.
        """
        return "/{0}/{1}/".format(self._meta.db_table, self.pk)

    def get_edit_url(self):
        """
        Return the edit url of an object.
        """
        return "/{0}/{1}/update/".format(self._meta.db_table, self.pk)

    def get_delete_url(self):
        """
        Return the delete url of an object.
        """
        return "/{0}/{1}/delete/".format(self._meta.db_table, self.pk)

    def get_create_url(self):
        """
        Return the delete url of an object.
        """
        return "/{0}/create/".format(self._meta.db_table)
