from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.util import ErrorList, ErrorDict
from django.shortcuts import (get_object_or_404, render, render_to_response,
                              redirect)

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.forms import (Nameserver, NameserverForm,
                                          NSDelegated)
from cyder.cydns.views import *


class NSView(object):
    model = Nameserver
    form_class = NameserverForm
    queryset = Nameserver.objects.all()
    extra_context = {'record_type': 'nameserver'}


class NSListView(NSView, CydnsListView):
    """ """
    # Wooo. Huge speed boost because of select_related
    queryset = Nameserver.objects.all().select_related()


class NSDeleteView(NSView, CydnsDeleteView):
    """ """


class NSDetailView(NSView, CydnsDetailView):
    template_name = "nameserver/nameserver_detail.html"


class NSCreateView(NSView, CydnsCreateView):
    """ """


class NSUpdateView(NSView, CydnsUpdateView):
    """ """


def update_ns(request, nameserver_pk):
    nameserver = get_object_or_404(Nameserver, pk=nameserver_pk)
    if request.method == "POST":
        form = NameserverForm(request.POST, instance=nameserver)
        try:
            if form.is_valid():
                server = form.cleaned_data['server']
                domain = form.cleaned_data['domain']
                if 'glue' in form.cleaned_data:
                    glue_type, glue_pk = form.cleaned_data['glue'].split('_')
                    try:
                        if glue_type == 'addr':
                            glue = AddressRecord.objects.get(pk=glue_pk)
                        elif glue_type == 'intr':
                            glue = StaticInterface.objects.get(pk=glue_pk)
                    except ObjectDoesNotExists, e:
                        raise ValidationError("Couldn't find glue: " + str(e))
                    nameserver.glue = glue
                nameserver.server = server
                nameserver.domain = domain
                nameserver.clean()
                nameserver.save()
        except ValidationError, e:
            form = Nameserver(instance=nameserver)
            if form._errors is None:
                form._errors = ErrorDict()
            form._errors['__all__'] = ErrorList(e.messages)

        return redirect(nameserver)
    else:
        form = NameserverForm(instance=nameserver)
    return render(request, "cydns/cydns_form.html", {
        'form': form
    })


def create_ns_delegated(request, domain):
    if request.method == "POST":
        form = NSDelegated(request.POST)
        domain = Domain.objects.get(pk=domain)
        if not domain:
            pass  # Fall through. Maybe send a message saying no domain?
        elif form.is_valid():
            server = form.cleaned_data['server']
            ip_str = form.cleaned_data['server_ip_address']
            was_delegated = domain.delegated
            if was_delegated:
                # Undelegate the domain to add address record.
                domain.delegated = False
                domain.save()
            if was_delegated:
                # Reset delegation status.
                domain.delegated = True
                domain.save()

    # Blank form for all else.
    form = NSDelegated()
    return render_to_response("nameserver/ns_delegated.html",
                              {'form': form, 'request': request})
