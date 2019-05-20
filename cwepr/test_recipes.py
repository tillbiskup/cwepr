import aspecd.tasks
import aspecd.io
import os
import cwepr.dataset


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
source = path+"/Messdaten/Recipe" \
              ".yaml"
#source = "/home/kirchner/nas/Praktikum/Messdaten/Recipe.yaml"

dts_fact = cwepr.dataset.DatasetFactory()
recipe = aspecd.tasks.Recipe()
recipe.dataset_factory = dts_fact
importer = aspecd.io.RecipeYamlImporter(source=source)
importer.import_into(recipe=recipe)

chef = aspecd.tasks.Chef(recipe=recipe)
try:
    chef.cook()
except:
    pass
print(recipe.tasks[6].properties['context'])

#print(list(recipe.datasets.values())[0].to_dict()['tasks'][8])
