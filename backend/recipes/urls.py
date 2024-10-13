from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'recipes'

router = routers.DefaultRouter()
router.register('tags', views.TagViewSet, basename='tag')
router.register('ingredients', views.IngredientViewSet, basename='ingredient')
router.register('recipes', views.RecipesViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
]
