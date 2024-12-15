from django.utils.timezone import localtime

SHOPPING_LIST = '{index}. {ingredient_name} - {sum} {measurement_unit}'

CASES = {
    'банка': ['банки', 'банок'],
    'батон': ['батона', 'батонов'],
    'веточка': ['веточки', 'веточек'],
    'горсть': ['горсти', 'горстей'],
    'капля': ['капли', 'капель'],
    'кусок': ['куска', 'кусков'],
    'стакан': ['стакана', 'стаканов'],
    'щепотка': ['щепотки', 'щепоток'],
}


def get_case(product, amount):
    """Функция для склонения единиц измерения продуктов."""
    if product not in CASES:
        return product
    if (amount % 100 in range(11, 20)) or (amount % 10 in [0, 5, 6, 7, 8, 9]):
        return CASES[product][1]
    if amount % 10 in [2, 3, 4]:
        return CASES[product][0]
    return product


def get_shopping_list(ingredients, recipes):
    """Функция для получения списка покупок."""
    return '\n'.join([
        f'Список покупок на {localtime().date().strftime("%d/%m/%y")}',
        '\nПродукты:',
        *map(
            lambda ingredient, index: (
                SHOPPING_LIST.format(
                    index=index,
                    ingredient_name=ingredient[
                        "ingredient__name"
                    ].capitalize(),
                    sum=ingredient["sum"],
                    measurement_unit=get_case(
                        ingredient["ingredient__measurement_unit"],
                        ingredient["sum"]
                    )
                )
            ),
            ingredients, range(1, ingredients.count() + 1)
        ),
        '\nДля блюд:',
        *recipes.values_list('name', flat=True)
    ])
