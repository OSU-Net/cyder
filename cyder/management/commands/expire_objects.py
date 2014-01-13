from django.core.management.base import BaseCommand

from cyder.models import MODEL_LIST
from cyder.base.models import ExpirableMixin

from datetime import datetime


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        now = datetime.now()
        for model in MODEL_LIST:
            if issubclass(model, ExpirableMixin):
                objects = model.objects.filter(expire__lte=now)
                for obj in objects:
                    obj.delete()
