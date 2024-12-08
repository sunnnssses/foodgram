from api.serializers import IngredientSerializer
from recipes.management.commands._uploader import UploaderBase


class Command(UploaderBase):
    serializer_class = IngredientSerializer
