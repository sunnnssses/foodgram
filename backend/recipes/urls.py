from django.urls import path

from .views import short_url_redirection

app_name = 'recipes'

urlpatterns = [
    path('s/<int:pk>', short_url_redirection, name='short_url')
]
