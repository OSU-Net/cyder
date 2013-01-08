import simplejson as json

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import messages
from django.forms.util import ErrorList
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import (StaticInterface,
                                                       StaticIntrKeyValue)
from cyder.cydhcp.keyvalue.utils import (get_attrs, update_attrs, get_aa,
                                         get_docstrings, dict_to_kv)
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain



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
    An view destined to be called by ajax to remove an attr.
    """
    #system = get_object_or_404(System, pk=system_pk)
    #intr = get_object_or_404(StaticInterface, pk=intr_pk)
    attr = get_object_or_404(StaticIntrKeyValue, pk=attr_pk)
    attr.delete()
    return HttpResponse("Attribute Removed.")


def edit_static_interface(request, intr_pk):
    # TODO, make sure the user has access to this system
    intr = get_object_or_404(StaticInterface, pk=intr_pk)
    system = intr.system
    attrs = intr.staticintrkeyvalue_set.all()
    aa = get_aa(StaticIntrKeyValue())
    docs = get_docstrings(StaticIntrKeyValue())
    if request.method == 'POST':
        interface_form = StaticInterfaceForm(request.POST, instance=intr)
        if interface_form.is_valid():
            try:
                # Handle key value stuff.
                kv = None
                kv = get_attrs(request.POST)
                update_attrs(kv, attrs, StaticIntrKeyValue, intr, 'intr')
                intr = interface_form.save()

                # Everything checks out. Clean and Save all the objects.
                intr.clean()
                intr.save()
            except ValidationError, e:
                interface_form._errors['__all__'] = ErrorList(e.messages)
                if kv:
                    attrs = dict_to_kv(kv, StaticIntrKeyValue)
                return render(request, 'static_intr/static_intr_edit.html', {
                    'form': interface_form,
                    'intr': intr,
                    'attrs': attrs,
                    'aa': json.dumps(aa),
                    'docs': docs,
                    'form_title': 'Edit Interface for System {0}'.format(
                        system),
                    'domain': intr.domain
                })
        else:
            return render(request, 'static_intr/static_intr_edit.html', {
                'form': interface_form,
                'intr': intr,
                'attrs': attrs,
                'aa': json.dumps(aa),
                'docs': docs,
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
            'attrs': attrs,
            'aa': json.dumps(aa),
            'docs': docs,
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


def quick_create(request, system_pk):
    # TODO, make sure the user has access to this system
    system = get_object_or_404(System, pk=system_pk)
    if request.method == 'POST':
        interface_form = StaticInterfaceQuickForm(request.POST)

        a, ptr, r = None, None, None
        if interface_form.is_valid():
            try:
                #mac = interface_form.cleaned_data['mac']
                if 'label' in interface_form.cleaned_data:
                    label = interface_form.cleaned_data['label']
                else:
                    label = ""
                mrange_pk = interface_form.cleaned_data['range']
                mrange = get_object_or_404(Range, pk=mrange_pk)
                network = mrange.network
                ip_type = network.ip_type
                vlan = network.vlan
                site = network.site

                networks = []
                for network in vlan.network_set.all():
                    if not network.site:
                        continue
                    if network.site.get_site_path() == site.get_site_path():
                        networks.append(network)
                if not networks:
                    raise ValidationError(
                        "No appropriate networks found. "
                        "Consider adding this interface manually.")

                ip = mrange.get_next_ip()
                if ip is None:
                    raise ValidationError(
                        "No appropriate IP found in {0} Vlan {1} "
                        "Range {2} - {3}. Consider adding this interface "
                        "manually.".format(site.name, vlan.name,
                                           mrange.start_str, mrange.end_str))

                expected_name = "{0}.{1}.mozilla.com".format(
                    vlan.name, site.get_site_path())
                try:
                    domain = Domain.objects.get(name=expected_name)
                except ObjectDoesNotExist, e:
                    raise ValidationError(
                        "The domain '{0}' doesn't seem to exist. "
                        "Consider creating this interface "
                        "manually.".format(expected_name))

                intr = StaticInterface(label=label, domain=domain,
                                       ip_str=str(ip), ip_type=ip_type,
                                       system=system)
                intr.full_clean()
                intr.save()
            except ValidationError, e:
                interface_form._errors['__all__'] = ErrorList(e.messages)
                return render(request, 'static_intr/static_intr_form.html', {
                    'form': interface_form,
                    'form_title': "Quick Interface Create for System "
                    "{0}".format(system)
                })
        else:
            return render(request, 'static_intr/static_intr_form.html', {
                'form': interface_form,
                'form_title': 'Quick Interface Create for System {0}'.format(
                    system)
            })

        messages.success(request, "Success! Interface Created.")
        return redirect(system)

    else:
        interface_form = StaticInterfaceQuickForm()
        return render(request, 'static_intr/static_intr_form.html', {
            'form': interface_form,
            'form_title': 'Quick Interface Create for System {0}'.format(
                system)
        })
