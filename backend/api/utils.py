from django.utils.timezone import localtime

SHOPPING_LIST = '{index}. {ingredient_name}, {units} - {sum}'


def get_shopping_list(ingredients, recipes):
    """Функция для получения списка покупок."""
    return '\n'.join([
        'Список покупок на {}'.format(localtime().date().strftime('%d/%m/%y')),
        '\nПродукты:',
        *(SHOPPING_LIST.format(
            index=index,
            ingredient_name=ingredient[
                'ingredient__name'
            ].capitalize(),
            units=ingredient['ingredient__measurement_unit'],
            sum=ingredient['sum']
        )for index, ingredient in enumerate(ingredients, 1)),
        '\nДля рецептов:',
        *recipes.values_list('name', flat=True)
    ])
