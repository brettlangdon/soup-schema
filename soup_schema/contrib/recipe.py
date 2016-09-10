from ..schema import Schema
from ..selector import Selector, AnySelector, AttrSelector


class RecipeSchema(Schema):
    # Publish data
    author = Selector('[itemprop=author]')
    categories = Selector('[itemprop=recipeCategory]', as_list=True)
    description = AnySelector([
        Selector('[itemprop=description]'),
        Selector('[name=og:description]'),
        Selector('[name=description]')
    ], required=True)
    name = AnySelector([
        Selector('[itemprop=name]'),
        Selector('[property=og:title]')
    ], required=True)
    recipe_yield = Selector('[itemprop=recipeYield]')

    # Recipe instructions
    ingredients = AnySelector([
        Selector('[itemprop=recipeIngredient]', as_list=True),
        Selector('[itemprop=ingredients]', as_list=True),
    ], required=True)
    instructions = Selector('[itemprop=recipeInstructions]', as_list=True, required=True)

    # Cooking time
    cook_time = AttrSelector('[itemprop=cookTime]', 'datetime')
    prep_time = AttrSelector('[itemprop=prepTime]', 'datetime')
    total_time = AttrSelector('[itemprop=totalTime]', 'datetime')

    # Nutrition
    calories = Selector('[itemprop=calories]')
    carbohydrate_content = Selector('[itemprop=carbohydrateContent]')
    cholesterol_content = Selector('[itemprop=cholesterolContent]')
    fat_content = Selector('[itemprop=fatContent]')
    protein_content = Selector('[itemprop=proteinContent]')
    sodium_content = Selector('[itemprop=sodiumContent]')
