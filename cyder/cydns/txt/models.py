from django.db import models

from cyder.cydns.models import CydnsRecord


class TXT(CydnsRecord):
    """
    >>> TXT(label=label, domain=domain, txt_data=txt_data)
    """
    id = models.AutoField(primary_key=True)
    txt_data = models.TextField(help_text="The text data for this record.")

    search_fields = ("fqdn", "txt_data")

    class Meta:
        db_table = "txt"
        # unique_together = ("domain", "label", "txt_data")
        # TODO
        # _mysql_exceptions.OperationalError: (1170, "BLOB/TEXT column
        # "txt_data" used in key specification without a key length")
        # Fix that ^

    def __str__(self):
        return "{0} TXT {1}".format(self.fqdn, self.txt_data)

    def __repr__(self):
        return "<TXT {0}>".format(self)

    def details(self):
        """For tables."""
        data = super(TXT, self).details()
        data['data'] = [
            ('Domain', 'domain__name', self.domain),
            ('Text', 'txt_data', self.txt_data)
        ]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'fqdn', 'datatype': 'string', 'editable': True},
            {'name': 'txt_data', 'datatype': 'string', 'editable': True},
        ]}

    @classmethod
    def get_api_fields(cls):
        data = super(TXT, cls).get_api_fields() + ['txt_data']
        return data

    def save(self, *args, **kwargs):
        self.full_clean()
        super(TXT, self).save(*args, **kwargs)

    def clean(self):
        super(TXT, self).clean()
        super(TXT, self).check_for_delegation()
        super(TXT, self).check_for_cname()
