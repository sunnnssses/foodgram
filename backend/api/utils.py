from django.utils.timezone import localtime


def get_shopping_list(ingredients, recipes):
    """Функция для получения списка покупок."""
    return '\n'.join([
        f'Список покупок на {localtime().date().strftime("%d/%m/%y")}',
        'Продукты:',
        *map(
            lambda ingredient: (
                f'{ingredient["index"]}. '
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["overall_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            ),
            ingredients
        ),
        'Для блюд:',
        *recipes
    ])
