from django.shortcuts import redirect


def short_url_redirection(request, pk):
    """Функция для перенаправления по короткой ссылке."""
    return redirect(request.build_absolute_uri(
        f'/recipes/{pk}/'
    ))
