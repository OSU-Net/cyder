from gettext import gettext as _
from string import Template

from django.db import models

from cyder.base.utils import transaction_atomic
from cyder.cydns.models import CydnsRecord, LabelDomainMixin
from cyder.cydns.validation import validate_txt_data


class TXT(LabelDomainMixin, CydnsRecord):
    """
    >>> TXT(label=label, domain=domain, txt_data=txt_data)
    """
    pretty_type = 'TXT'

    id = models.AutoField(primary_key=True)
    txt_data = models.TextField(
        help_text="The text data for this record.",
        validators=[validate_txt_data]
    )
    ctnr = models.ForeignKey("cyder.Ctnr", null=False,
                             verbose_name="Container")

    search_fields = ("fqdn", "txt_data")

    class Meta:
        app_label = 'cyder'
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

    def __unicode__(self):
        return u'{} TXT {}'.format(self.fqdn, self.txt_data)

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
    def escaped_txt_data(self):
        return self.txt_data.replace('\\', '\\\\').replace('"', '\\"')

    @property
    def rdtype(self):
        return 'TXT'

    def bind_render_record(self, pk=False):
        TXT_LINE_LENGTH = 120

        def length_format(line):
            if len(line) <= TXT_LINE_LENGTH:
                return '"{0}"'.format(line)
            return (('"%s"' % line[:TXT_LINE_LENGTH]) + "\n"
                    + length_format(line[TXT_LINE_LENGTH:]))

        template = Template(self.template).substitute(**self.justs)
        bind_name = self.fqdn + "."
        if not self.ttl:
            self.ttl = 3600

        txt_lines = self.escaped_txt_data.split('\n')
        txt_data = ""
        if len(txt_lines) > 1:
            for line in txt_lines:
                txt_data += length_format(line) + "\n"
        else:
            txt_data = length_format(self.escaped_txt_data)

        txt_data = txt_data.strip('\n')
        if '\n' in txt_data:
            txt_data = '(\n{0})'.format(txt_data).replace('\n', '\n    ')

        return template.format(
            bind_name=bind_name, ttl=self.ttl, rdtype=self.rdtype,
            rdclass='IN', txt_data=txt_data
        )

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(TXT, self).save(*args, **kwargs)
