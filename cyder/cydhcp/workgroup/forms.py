from django import forms
from django.db.models.query import EmptyQuerySet

from cyder.cydhcp.workgroup.models import Workgroup


class WorkgroupForm(forms.ModelForm):
    class Meta:
        model = Workgroup
