import json
from django.core.management.base import BaseCommand

class UploaderBase(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        with open(options['path'], 'r', encoding='utf-8') as f:
            data = self.serializer_class(
                data=json.load(f),
                many=True
            )
            data.is_valid(raise_exception=True)
            data.save()