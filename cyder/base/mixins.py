import os
import fcntl
from string import Template

from django.core.urlresolvers import NoReverseMatch, reverse
from django.db.models.loading import get_model
from django.forms import ModelChoiceField, HiddenInput
from django import forms

from cyder.base.utils import filter_by_ctnr


class DisplayMixin(object):
    # Knobs
    justs = {
        'pk_just':      10,
        'rhs_just':     1,
        'ttl_just':     6,
        'rdtype_just':  7,
        'rdclass_just': 3,
        'prio_just':    2,
        'lhs_just':     61,
        'extra_just':   1
    }

    def bind_render_record(self, pk=False, custom=None):
        kwargs = vars(self)
        if custom:
            for key, value in custom.items():
                kwargs[key] = value

        template = Template(self.template).substitute(**self.justs)
        bind_name = self.fqdn + "."

        if not self.ttl:
            self.ttl = 3600

        return template.format(bind_name=bind_name, rdtype=self.rdtype,
                               rdclass='IN', **kwargs)


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
        return reverse('delete')

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


class UsabilityFormMixin(object):
    def append_required_all(self):
        for fieldname, field in self.fields.items():
            if self.fields[fieldname].required is True:
                if self.fields[fieldname].label is None:
                    fname = fieldname.replace('_', ' ')
                    self.fields[fieldname].label = fname.capitalize() + '*'
                else:
                    self.fields[fieldname].label += '*'

    def alphabetize_all(self):
        for fieldname, field in self.fields.items():
            if hasattr(field, 'queryset'):
                self.fields[fieldname].queryset = field.queryset.order_by(
                    *field.queryset.model.display_fields)

    def filter_by_ctnr_all(self, request, allow_reverse_domains=False):
        from cyder.core.ctnr.models import Ctnr
        from cyder.cydns.domain.models import Domain
        ctnr = request.session['ctnr']
        for fieldname, field in self.fields.items():
            if not hasattr(field, 'queryset'):
                continue

            queryset = self.fields[fieldname].queryset
            if queryset.model is Ctnr:
                ctnrs = set(c.pk for c in request.session['ctnrs'])
                for pk in [1, 2]:
                    if pk in ctnrs:
                        ctnrs.remove(pk)

                if self.fields[fieldname].initial:
                    ctnrs.add(self.fields[fieldname].initial.pk)

                queryset = queryset.filter(pk__in=ctnrs)
            else:
                queryset = filter_by_ctnr(ctnr=ctnr,
                                          objects=field.queryset).distinct()

            if queryset.model == Domain and not allow_reverse_domains:
                queryset = queryset.filter(is_reverse=False)

            if queryset.count() == 1:
                self.fields[fieldname].initial = queryset[0]

            self.fields[fieldname].queryset = queryset

    def autoselect_system(self):
        System = get_model('cyder', 'system')
        if 'system' in self.initial:
            self.fields['system'] = ModelChoiceField(
                widget=HiddenInput(),
                empty_label='',
                queryset=System.objects.filter(pk=int(self.initial['system'])))
        elif 'system' in self.fields:
            del(self.fields['system'])

    def autoselect_ctnr(self, request):
        if 'ctnr' not in self.fields:
            return

        ctnr = request.session['ctnr']
        if ctnr.name != "global":
            if 'ctnr' not in self.initial:
                self.fields['ctnr'].initial = request.session['ctnr']
            self.fields['ctnr'].widget = HiddenInput()

    def make_usable(self, request):
        self.autoselect_system()
        self.autoselect_ctnr(request)
        if 'ctnr' in request.session:
            self.filter_by_ctnr_all(request)
        self.alphabetize_all()
        self.append_required_all()


class MutexMixin(object):
    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unlock()

    def lock(self):
        if not os.path.exists(os.path.dirname(self.lock_file)):
            os.makedirs(os.path.dirname(self.lock_file))
        self.log_debug("Attempting to lock {0}..."
                 .format(self.lock_file))

        self.lock_fd = open(self.lock_file, 'w')

        try:
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as exc_value:
            self.lock_fd.close()
            # IOError: [Errno 11] Resource temporarily unavailable
            if exc_value[0] == 11:
                with open(self.pid_file, 'r') as pid_fd:
                    self._lock_failure(pid_fd.read())
            else:
                raise

        self.log_debug("Lock acquired")

        try:
            with open(self.pid_file, 'w') as pid_fd:
                pid_fd.write(unicode(os.getpid()))
        except IOError as exc_value:
            # IOError: [Errno 2] No such file or directory
            if exc_value[0] == 2:
                raise Exception("Failed to acquire lock on {0}, but the "
                                "the process that has it hasn't written "
                                "the PID file {1} yet."
                                .format(self.lock_file, self.pid_file))
            else:
                raise

    def unlock(self):
        if not self.lock_fd:
            return False

        self.log_debug("Releasing lock ({0})...".format(self.lock_file))

        fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
        self.lock_fd.close()
        os.remove(self.pid_file)
        os.remove(self.lock_file)

        self.log_debug("Unlock complete")
        return True

    def _lock_failure(self, pid):
        raise Exception('Failed to acquire lock on {0}. Process {1} currently '
                        'has it.'.format(self.lock_file, pid))
