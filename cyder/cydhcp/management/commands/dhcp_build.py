from cyder.cydhcp.build.builder import build
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        build()
