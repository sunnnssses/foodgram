from recipes.management.commands._uploader import UploaderBase
from recipes.models import Tag


class Command(UploaderBase):
    model = Tag
