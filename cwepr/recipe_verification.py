"""Minimal code for running an recipe driven evaluation example."""


import os

import aspecd.tasks
import aspecd.io

import cwepr.dataset


PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SOURCE_1 = PATH + "/data/recipe_verification1.yaml"
SOURCE_2 = PATH + "/data/recipe_verification2.yaml"

SOURCELIST = [SOURCE_1, SOURCE_2]

for source in SOURCELIST:
    DTS_FACT = cwepr.dataset.DatasetFactory()
    RECIPE = aspecd.tasks.Recipe()
    RECIPE.dataset_factory = DTS_FACT
    IMPORTER = aspecd.io.RecipeYamlImporter(source=source)
    IMPORTER.import_into(recipe=RECIPE)

    CHEF = aspecd.tasks.Chef(recipe=RECIPE)
    CHEF.cook()

