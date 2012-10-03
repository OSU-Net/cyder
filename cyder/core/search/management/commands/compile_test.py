from django.core.management.base import BaseCommand, CommandError
from cyder.core.search.compiler import compiler


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
