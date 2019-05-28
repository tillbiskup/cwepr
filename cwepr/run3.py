import os.path
import cwepr.dataset
import cwepr.analysis
import cwepr.processing
import cwepr.io


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

dts = cwepr.dataset.Dataset()
dts.import_from_file((path+"/Messdaten/1_No1-dunkel"))

dts_standard = cwepr.dataset.Dataset()
dts_standard.import_from_file((path+"/Messdaten/LiLiF-20180628"))

get_B0_step = cwepr.analysis.FieldCorrectionValueFinding()
get_B0_analysis = dts_standard.analyse(get_B0_step)
delta_b0 = get_B0_analysis.result

print(delta_b0)

correct = cwepr.processing.FieldCorrection()
correct.parameters["correction_value"] = delta_b0
dts.process(correct)
