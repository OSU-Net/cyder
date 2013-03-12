from string import Template

from django.core.urlresolvers import NoReverseMatch, reverse


class DisplayMixin(object):
    # Knobs
    justs = {
        'pk_just': 10,
        'rhs_just': 1,
        'ttl_just': 1,
        'rdtype_just': 4,
        'rdclass_just': 3,
        'prio_just': 1,
        'lhs_just': 40,
        'extra_just': 1
    }

    def bind_render_record(self, pk=False):
        template = Template(self.template).substitute(**self.justs)
        bind_name = self.fqdn + "."
        if not self.ttl:
            self.ttl = 3600
        return template.format(bind_name=bind_name, rdtype=self.rdtype,
                               rdclass='IN', **vars(self))


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
        Return the 'list' url of an object. Class method since don't
        need specific instance of object.
        """
        return reverse(cls._meta.db_table)

    @classmethod
    def get_create_url(cls):
        """Return the create url of the type of object (to be posted to)."""
        return cls.get_list_url()

    def get_update_url(self):
        """Return the update url of an object."""
        return reverse(self._meta.db_table + '-update', args=[self.pk])

    def get_delete_url(self):
        """Return the delete url of an object."""
        return reverse(self._meta.db_table + '-delete', args=[self.pk])

    def get_detail_url(self):
        """Return the detail url of an object."""
        try:
            return reverse(self._meta.db_table + '-detail', args=[self.pk])
        except NoReverseMatch:
            return ''

    def get_table_update_url(self):
        """Return the editableGrid update url of an object."""
        try:
            return reverse(self._meta.db_table + '-table-update',
                           args=[self.pk])
        except NoReverseMatch:
            return ''

    def details(self):
        """
        Return base details with generic postback URL for editable tables.
        """
        return {'url': self.get_table_update_url()}
