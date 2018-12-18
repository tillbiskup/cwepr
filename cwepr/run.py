import os.path
import cwepr.dataset


dts = cwepr.dataset.Dataset()
path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dts.import_from_file((path+"/Messdaten/1_No1-dunkel"))
print(dts.metadata.to_dict())
