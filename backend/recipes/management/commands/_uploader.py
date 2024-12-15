import json

from django.core.management.base import BaseCommand


class UploaderBase(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        with open(options['path'], 'r', encoding='utf-8') as f:
            self.model.objects.bulk_create(
                [self.model(**data) for data in json.load(f)],
                ignore_conflicts=True
            )
