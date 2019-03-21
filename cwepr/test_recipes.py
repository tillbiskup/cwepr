import aspecd.tasks
import aspecd.io
import os
import cwepr.io


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
source = path+"/Messdaten/Recipe.yaml"
imp_fact = cwepr.io.ImporterFactoryEPR()
recipe = aspecd.tasks.Recipe()
recipe.importer_factory = imp_fact
importer = aspecd.io.RecipeYamlImporter(source=source)
importer.import_into(recipe=recipe)

chef = aspecd.tasks.Chef(recipe=recipe)
chef.cook()
