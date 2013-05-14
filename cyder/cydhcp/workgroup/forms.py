from django import forms

from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupKeyValue


class WorkgroupForm(forms.ModelForm):

    class Meta:
        model = Workgroup


class WorkgroupKeyValueForm(forms.ModelForm):

    class Meta:
        model = WorkgroupKeyValue
        exclude = ("is_quoted",)
