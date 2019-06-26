"""Minimal code for running an recipe driven evaluation example."""


import os

import aspecd.tasks
import aspecd.io

import cwepr.dataset


PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SOURCE = PATH + "/Messdaten/Recipe2.yaml"

DTS_FACT = cwepr.dataset.DatasetFactory()
RECIPE = aspecd.tasks.Recipe()
RECIPE.dataset_factory = DTS_FACT
IMPORTER = aspecd.io.RecipeYamlImporter(source=SOURCE)
IMPORTER.import_into(recipe=RECIPE)

CHEF = aspecd.tasks.Chef(recipe=RECIPE)
CHEF.cook()
