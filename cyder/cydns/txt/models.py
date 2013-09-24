from gettext import gettext as _
from string import Template

from django.db import models

from cyder.cydns.models import CydnsRecord, LabelDomainMixin
from cyder.cydns.validation import validate_txt_data


class TXT(CydnsRecord, LabelDomainMixin):
    """
    >>> TXT(label=label, domain=domain, txt_data=txt_data)
    """

    id = models.AutoField(primary_key=True)
    txt_data = models.TextField(
        help_text="The text data for this record.",
        validators=[validate_txt_data]
    )

    search_fields = ("fqdn", "txt_data")

    class Meta:
        db_table = 'txt'
        # unique_together = ("domain", "label", "txt_data")
        # TODO
        # _mysql_exceptions.OperationalError: (1170, "BLOB/TEXT column
        # "txt_data" used in key specification without a key length")
        # Fix that ^

    def details(self):
        """For tables."""
        data = super(TXT, self).details()
        data['data'] = [
            ('Label', 'label', self.label),
            ('Domain', 'domain__name', self.domain),
            ('Text', 'txt_data', self.txt_data)
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'label', 'datatype': 'string', 'editable': True},
            {'name': 'domain', 'datatype': 'string', 'editable': True},
            {'name': 'txt_data', 'datatype': 'string', 'editable': True},
        ]}

    template = _("{bind_name:$lhs_just} {ttl:$ttl_just}  "
                 "{rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {txt_data:$rhs_just}")

    @property
    def rdtype(self):
        return 'TXT'

    def bind_render_record(self, pk=False):
        template = Template(self.template).substitute(**self.justs)
        bind_name = self.fqdn + "."
        if not self.ttl:
            self.ttl = 3600

        txt_lines = self.txt_data.split('\n')
        if len(txt_lines) > 1:
            txt_data = '('
            for line in self.txt_data.split('\n'):
                txt_data += '"{0}"\n'.format(line)
            txt_data = txt_data.strip('\n') + ')'
        else:
            txt_data = '"{0}"'.format(self.txt_data)

        return template.format(
            bind_name=bind_name, ttl=self.ttl, rdtype=self.rdtype,
            rdclass='IN', txt_data=txt_data
        )
