from django.http import Http404
from django.shortcuts import redirect

from .models import Recipe


def short_url_redirection(request, pk):
    """Функция для перенаправления по короткой ссылке."""
    if not Recipe.objects.filter(pk=pk).exists():
        raise Http404(
            'Рецепт, соответствующий короткой ссылке {}, не найден.'.format(
                request.get_full_path()
            )
        )
    return redirect(request.build_absolute_uri(
        f'/recipes/{pk}/'
    ))
