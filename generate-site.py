from datetime import datetime
from pathlib import Path
from pprint import pformat, pprint

from slugify import slugify
from unicat import UnicatTransform
from unicat.utils import DuckObject

from config import get_unicat

plurals = {
    "blik": "blikken",
    "blikje": "blikjes",
    "blokje": "blokjes",
    "bosje": "bosjes",
    "hand": "handen",
    "handje": "handjes",
    "plak": "plakken",
    "pot": "potten",
    "stengel": "stengels",
    "stokje": "stokjes",
    "stronk": "stronken",
    "takje": "takjes",
    "teen": "tenen",
    "teentje": "teentjes",
    "vel": "vellen",
    "zakjes": "zakjes",
}


def pluralize(term, q):
    if q != 1 and term in plurals:
        return plurals[term]
    return term


def format_field_value(recordfield):
    if recordfield.field.type == "image":
        transform = UnicatTransform(
            resize="width", width=600, type="jpg", dpr=2, optimize=True
        )
        transform.merge(recordfield.default_transform)
        recordfield.download_transformed(transform, recordfield.pathname)
        return f"/files{recordfield.pathname}"
    return recordfield.value


def format_recipe(context):
    def format_ingredient(ingredient):
        i = DuckObject(**ingredient)
        return ", ".join(
            part
            for part in [
                i.ingredient,
                " ".join(
                    part
                    for part in [
                        f"{i.ingredient_q:.100g}" if i.ingredient_q else None,
                        pluralize(i.ingredient_unit, i.ingredient_q),
                    ]
                    if part
                ),
                i.ingredient_preparation,
            ]
            if part
        )

    recipe = DuckObject(**context)
    return f"""---
type: eten

title: {recipe.name}
slug: {recipe.slug}
date: "{recipe.created_on}"
description: {recipe.intro}
image: {recipe.recipe_image}

bereidingstijd: {recipe.duration}
voorbereiding: {recipe.recipe_preparation}
personen: {recipe.servings}
keuken: {recipe.kitchen}
waardering: {recipe.rating}
soort:
{"\n".join(f"- {type}" for type in recipe.recipe_type)}
tags:
{"\n".join(f"- {tag}" for tag in recipe.tags)}

---

## Ingrediënten

*voor {recipe.servings} {"persoon" if recipe.servings == 1 else "personen"}*

{
        "\n".join(
            f"* {format_ingredient(ingredient)}"
            for ingredient in recipe.ingredients
            if len(format_ingredient(ingredient))
        )
    }

## Bereiding

{recipe.preparation}
{
        f'''
### Notes

{recipe.notes}
'''
        if recipe.notes
        else ""
    }
{
        f'''
#### Bron

{recipe.source}
'''
        if recipe.source
        else ""
    }
"""


def format_drink(context):
    drink = DuckObject(**context)
    return f"""---
type: drinken

title: {drink.name}
slug: {drink.slug}
date: "{drink.created_on}"
description: {drink.intro}
image: {drink.drink_image}

soort: {drink.drink_type}
land: {drink.country}
waardering: {drink.rating}
tags:
{"\n".join(f"- {tag}" for tag in drink.tags)}

---

{drink.description}
{
        f'''
### Notes

{drink.notes}
'''
        if drink.notes
        else ""
    }
"""


def format_restaurant(context):
    restaurant = DuckObject(**context)
    return f"""---
type: uit-eten

title: {restaurant.name}
slug: {restaurant.slug}
date: "{restaurant.created_on}"
description: {restaurant.intro}
image: {restaurant.restaurant_image}

keuken: {restaurant.kitchen}
plaats: {restaurant.city}
waardering: {restaurant.rating}
tags:
{"\n".join(f"- {tag}" for tag in restaurant.tags)}

---

{restaurant.description}
{
        f'''
### Notes

{restaurant.notes}
'''
        if restaurant.notes
        else ""
    }
{
        f'''
#### Adres

{restaurant.address}
'''
        if restaurant.address
        else ""
    }
{
        f'''
<{restaurant.url}>
'''
        if restaurant.url
        else ""
    }
"""


types = {
    "recipe": ("eten", format_recipe),
    "drink": ("drinken", format_drink),
    "restaurant": ("uit-eten", format_restaurant),
}


def main():
    unicat = get_unicat("LIVE.lekker", "./site/files")

    print()
    print(unicat.project.name)
    print("=" * len(unicat.project.name))
    print()

    type_counter = {}

    for record in unicat.walk_record_tree(ordering=unicat.project.default_ordering):
        if record.definition.name not in types:
            continue

        fields = record.fields["nl"]
        slug = slugify(fields["name"].value)
        created_on = datetime.fromtimestamp(record.created_on)

        context = {
            name: format_field_value(recordfield)
            for name, recordfield in fields.items()
        }
        context["slug"] = slug
        context["created_on"] = created_on.strftime("%Y-%m-%d")

        folder, formatter = types[record.definition.name]
        filename = f"{slug}.md"
        print(f"{folder}:", slug)
        with open(Path("site", folder, filename), "w") as f:
            f.write(formatter(context) + "\n")

        if record.definition.name not in type_counter:
            type_counter[record.definition.name] = 0
        type_counter[record.definition.name] += 1

    print()
    pprint(type_counter)
    print()


if __name__ == "__main__":
    main()
