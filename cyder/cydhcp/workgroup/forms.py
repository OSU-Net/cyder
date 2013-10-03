from django import forms

from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupAV


class WorkgroupForm(forms.ModelForm):

    class Meta:
        model = Workgroup


class WorkgroupAVForm(forms.ModelForm):
    workgroup = forms.ModelChoiceField(
        queryset=Workgroup.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = WorkgroupAV
        exclude = ("is_quoted",)
