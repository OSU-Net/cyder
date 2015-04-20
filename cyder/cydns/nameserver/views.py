from django.core.exceptions import ValidationError
from django.forms.util import ErrorList, ErrorDict
from django.shortcuts import (get_object_or_404, render, render_to_response,
                              redirect)

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.forms import (Nameserver, NameserverForm,
                                          NSDelegated)
from cyder.cydns.views import cy_render


class NSView(object):
    model = Nameserver
    form_class = NameserverForm
    queryset = Nameserver.objects.all()
    extra_context = {'obj_type': 'nameserver'}


def create_ns_delegated(request, domain):
    if request.method == "POST":
        form = NSDelegated(request.POST)
        domain = Domain.objects.get(pk=domain)
        if not domain:
            pass  # Fall through. Maybe send a message saying no domain?
        elif form.is_valid():
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
    return cy_render("nameserver/ns_delegated.html",
                              {'form': form, 'request': request})
