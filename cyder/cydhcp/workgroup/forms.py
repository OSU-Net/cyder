from django import forms

from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupAV


class WorkgroupForm(forms.ModelForm):

    class Meta:
        model = Workgroup


class WorkgroupAVForm(forms.ModelForm):
    entity = forms.ModelChoiceField(
        queryset=Workgroup.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = WorkgroupAV
        fields = ('entity', 'attribute', 'value')
