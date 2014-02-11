from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app

from cyder.base.models import ExpirableMixin

from datetime import datetime


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        now = datetime.now()
        for model in get_models(get_app('cyder')):
            if issubclass(model, ExpirableMixin):
                objects = model.objects.filter(expire__lte=now)
                for obj in objects:
                    obj.delete()
