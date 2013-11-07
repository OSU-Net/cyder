from django import forms

from cyder.base.eav.forms import get_eav_form
from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupAV


class WorkgroupForm(forms.ModelForm):

    class Meta:
        model = Workgroup


WorkgroupAVForm = get_eav_form(WorkgroupAV, Workgroup)
