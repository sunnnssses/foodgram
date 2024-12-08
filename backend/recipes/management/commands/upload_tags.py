from api.serializers import TagSerializer
from recipes.management.commands._uploader import UploaderBase


class Command(UploaderBase):
    serializer_class = TagSerializer
