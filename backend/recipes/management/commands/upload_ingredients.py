from recipes.models import Ingredient

from ._uploader import UploaderBase


class Command(UploaderBase):
    model = Ingredient
