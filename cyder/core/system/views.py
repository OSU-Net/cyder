from django import forms
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect


from cyder.base.utils import tablefy, qd_to_py_dict
from cyder.core.system.models import System
from cyder.core.system.forms import SystemForm
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.forms import DynamicInterfaceForm
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.forms import StaticInterfaceForm


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
        'system_table': tablefy([system]),
        'attrs_table': tablefy(attrs),
        'static_intr_tables': static_intr,
        'dynamic_intr_tables': dynamic_intr,
        'obj_type': 'system',
        'obj': system,
    })


def system_create_view(request):
    system_form = SystemForm()
    static_form = StaticInterfaceForm()
    static_form.fields['system'].widget = forms.HiddenInput()
    dynamic_form = DynamicInterfaceForm()
    dynamic_form.fields['system'].widget = forms.HiddenInput()
    dynamic_form.fields['ctnr'].widget = forms.HiddenInput()

    if request.POST:
        post_data = qd_to_py_dict(request.POST)
        system_data = {}
        system_data['name'] = post_data.pop('name', None)
        system_data['interface_type'] = post_data.pop('interface_type', None)
        system_form = SystemForm(system_data)
        post_data['ctnr'] = request.session['ctnr'].id

        if system_form.is_valid():
            system = system_form.save()
            post_data['system'] = system.id

        else:
            system = None

        if system_data['interface_type'] is not None:

            if system_data['interface_type'] == 'Static':
                static_form = StaticInterfaceForm(post_data)

                if static_form.is_valid():
                    static_form.save()

                else:
                    if system:
                        system.delete()
                    static_form.fields['system'].widget = forms.HiddenInput()
                    dynamic_form = DynamicInterfaceForm()
                    dynamic_form.fields['system'].widget = forms.HiddenInput()
                    dynamic_form.fields['ctnr'].widget = forms.HiddenInput()

                    return render(request, 'system/system_create.html', {
                        'system_form': system_form,
                        'static_form': static_form,
                        'dynamic_form': dynamic_form})

            if system_data['interface_type'] == 'Dynamic':
                dynamic_form = DynamicInterfaceForm(post_data)

                if dynamic_form.is_valid():
                    dynamic_form.save()

                else:
                    if system:
                        system.delete()
                    static_form = StaticInterfaceForm()
                    static_form.fields['system'].widget = forms.HiddenInput()
                    dynamic_form.fields['system'].widget = forms.HiddenInput()
                    dynamic_form.fields['ctnr'].widget = forms.HiddenInput()

                    return render(request, 'system/system_create.html', {
                        'system_form': system_form,
                        'static_form': static_form,
                        'dynamic_form': dynamic_form})

            return redirect(reverse('system-detail', args=[system.id]))

        else:
            return render(request, 'system/system_create.html', {
                'system_form': system_form,
                'static_form': static_form,
                'dynamic_form': dynamic_form})

    else:

        return render(request, 'system/system_create.html', {
            'system_form': system_form,
            'static_form': static_form,
            'dynamic_form': dynamic_form})
