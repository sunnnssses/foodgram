from recipes.management.commands._uploader import UploaderBase
from recipes.models import Ingredient


class Command(UploaderBase):
    model = Ingredient
