from recipes.models import Tag

from ._uploader import UploaderBase


class Command(UploaderBase):
    model = Tag
