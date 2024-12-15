from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'api'

router = routers.DefaultRouter()
router.register('tags', views.TagViewSet, basename='tag')
router.register('ingredients', views.IngredientViewSet, basename='ingredient')
router.register('recipes', views.RecipesViewSet, basename='recipe')
router.register('users', views.FoodgramUserViewSet)

urlpatterns = [
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include(router.urls)),
    path('s/<str:short_url>', views.short_url_redirection, name='short_url')
]
