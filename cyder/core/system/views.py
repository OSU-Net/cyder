from django import forms
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect


from cyder.base.utils import tablefy, qd_to_py_dict
from cyder.core.system.models import System
from cyder.core.system.forms import ExtendedSystemForm
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.forms import DynamicInterfaceForm
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.forms import StaticInterfaceForm
from cyder.cydhcp.validation import MAC_ERR


def system_detail(request, pk):
    system = get_object_or_404(System, pk=pk)
    attrs = system.systemkeyvalue_set.all()
    dynamic = DynamicInterface.objects.filter(system=system)
    static = StaticInterface.objects.filter(system=system)
    static_intr = []
    dynamic_intr = []
    for intr in static:
        static_intr.append((tablefy((intr,)),
                            tablefy(intr.staticintrkeyvalue_set.all())))
    for intr in dynamic:
        dynamic_intr.append((tablefy((intr,)),
                             tablefy(intr.dynamicintrkeyvalue_set.all())))
    return render(request, 'system/system_detail.html', {
        'system': system,
        'system_table': tablefy([system], info=False),
        'attrs_table': tablefy(attrs),
        'static_intr_tables': static_intr,
        'dynamic_intr_tables': dynamic_intr,
        'obj_type': 'system',
        'obj': system,
    })


def system_create_view(request):
    system_form = ExtendedSystemForm()
    static_form = StaticInterfaceForm()
    dynamic_form = DynamicInterfaceForm()

    if request.POST:
        post_data = qd_to_py_dict(request.POST)
        system_data = {}
        system_data['name'] = post_data.pop('name', None)
        system_data['interface_type'] = post_data.pop('interface_type', None)
        system_form = ExtendedSystemForm(system_data)
        post_data['ctnr'] = request.session['ctnr'].id

        if system_form.is_valid():
            system = system_form.save()
            post_data['system'] = system.id

        else:
            system = None

        if system_data.get('interface_type', '') is None:
            if system:
                system.delete()

        else:
            if system_data.get('interface_type', '') == 'Static':
                form = StaticInterfaceForm(post_data)
                static_form = form
            elif system_data.get('interface_type', '') == 'Dynamic':
                form = DynamicInterfaceForm(post_data)
                dynamic_form = form

            if form.is_valid():
                form.save()
                return redirect(reverse('system-detail', args=[system.id]))
            else:
                if '__all__' in form.errors and (
                        MAC_ERR in form.errors['__all__']):
                    form.errors['__all__'].remove(MAC_ERR)
                    if 'mac' not in form.errors:
                        form.errors['mac'] = []
                    if MAC_ERR not in form.errors['mac']:
                        form.errors['mac'].append(MAC_ERR)

                if system:
                    system.delete()

    static_form.fields['system'].widget = forms.HiddenInput()
    dynamic_form.fields['system'].widget = forms.HiddenInput()
    dynamic_form.fields['ctnr'].widget = forms.HiddenInput()

    static_form.make_usable(request.session['ctnr'])
    dynamic_form.make_usable(request.session['ctnr'])

    return render(request, 'system/system_create.html', {
        'system_form': system_form,
        'static_form': static_form,
        'dynamic_form': dynamic_form})
