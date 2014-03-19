import json as json

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import messages
from django.forms.util import ErrorList
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from cyder.base.views import cy_detail
from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.forms import StaticInterfaceForm
from cyder.cydhcp.interface.static_intr.models import (StaticInterface,
                                                       StaticInterfaceAV)
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain


def static_intr_detail(request, pk):
    static_interface = get_object_or_404(StaticInterface, pk=pk)

    return cy_detail(request, StaticInterface,
                     'static_intr/static_intr_detail.html', {
                     'Attributes': 'staticinterfaceav_set',
                     }, pk=pk, obj=static_interface)


def detail_static_interface(reqeust, intr_pk):
    intr = get_object_or_404(StaticInterface, pk=intr_pk)
    system = intr.system
    return redirect(system)


def delete_static_interface(reqeust, intr_pk):
    intr = get_object_or_404(StaticInterface, pk=intr_pk)
    system = intr.system
    try:
        intr.delete()
    except ValidationError:
        pass
    return redirect(system)


def delete_attr(request, attr_pk):
    """
    A view destined to be called by ajax to remove an attr.
    """
    #system = get_object_or_404(System, pk=system_pk)
    #intr = get_object_or_404(StaticInterface, pk=intr_pk)
    attr = get_object_or_404(StaticInterfaceAV, pk=attr_pk)
    attr.delete()
    return HttpResponse("Attribute Removed.")


def edit_static_interface(request, intr_pk):
    # TODO, make sure the user has access to this system
    intr = get_object_or_404(StaticInterface, pk=intr_pk)
    system = intr.system
    if request.method == 'POST':
        interface_form = StaticInterfaceForm(request.POST, instance=intr)
        if interface_form.is_valid():
            try:
                intr = interface_form.save()

                # Everything checks out. Clean and Save all the objects.
                intr.clean()
                intr.save()
            except ValidationError, e:
                interface_form._errors['__all__'] = ErrorList(e.messages)
                return render(request, 'static_intr/static_intr_edit.html', {
                    'form': interface_form,
                    'intr': intr,
                    'form_title': 'Edit Interface for System {0}'.format(
                        system),
                    'domain': intr.domain
                })
        else:
            return render(request, 'static_intr/static_intr_edit.html', {
                'form': interface_form,
                'intr': intr,
                'form_title': 'Edit Interface for System {0}'.format(
                    system),
                'domain': intr.domain
            })

        messages.success(request, "Success! Interface Updated.")
        return redirect(intr.get_update_url())

    else:
        interface_form = StaticInterfaceForm(instance=intr)
        return render(request, 'static_intr/static_intr_edit.html', {
            'form': interface_form,
            'intr': intr,
            'form_title': 'Edit Interface for System {0}'.format(system),
            'domain': intr.domain
        })


def create_static_interface(request, system_pk):
    # TODO, make sure the user has access to this system
    system = get_object_or_404(System, pk=system_pk)
    if request.method == 'POST':
        interface_form = StaticInterfaceForm(request.POST)
        interface_form.instance.system = system

        a, ptr, r = None, None, None
        if interface_form.is_valid():
            try:
                intr = interface_form.instance
                intr.system = system
                intr.full_clean()
                intr.save()
            except ValidationError, e:
                interface_form._errors['__all__'] = ErrorList(e.messages)
                return render(request, 'static_intr/static_intr_form.html', {
                    'form': interface_form,
                    'form_title': 'New Interface for System {0}'.format(
                        system)
                })
        else:
            return render(request, 'static_intr/static_intr_form.html', {
                'form': interface_form,
                'form_title': 'New Interface for System {0}'.format(system)
            })

        messages.success(request, "Success! Interface Created.")
        return redirect(system)

    else:
        interface_form = StaticInterfaceForm()
        return render(request, 'static_intr/static_intr_form.html', {
            'form': interface_form,
            'form_title': 'New Interface for System {0}'.format(system)
        })
