import os.path
import cwepr.dataset
import cwepr.analysis
import cwepr.processing
import cwepr.plotting
import cwepr.io


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
source = path+"/Messdaten/1_No1-dunkel"
source2 = path+"/Messdaten/LiLiF-20180628"

dts = cwepr.dataset.Dataset()
importer_factory = cwepr.io.ImporterFactoryEPR()
importer = importer_factory.get_importer(source=source)

dts_standard = cwepr.dataset.Dataset()
importer_factory = cwepr.io.ImporterFactoryEPR()
importer2 = importer_factory.get_importer(source=source2)

dts.import_from(importer)
dts_standard.import_from(importer2)

nu_value = dts_standard.metadata.bridge.mw_frequency.value
get_B0_step = cwepr.analysis.FieldCorrectionValueFinding(nu_value)
get_B0_analysis = dts_standard.analyse(get_B0_step)
delta_b0 = get_B0_analysis.results["Delta_B0"]

correct = cwepr.processing.FieldCorrection(delta_b0)
dts.process(correct)

get_baseline_polynome_step = cwepr.analysis.BaselineFitting(0)
get_baseline_polynome_analysis = dts.analyse(get_baseline_polynome_step)
polynome_coeffs0 = get_baseline_polynome_analysis.results["Fit_Coeffs"]

get_baseline_polynome_step = cwepr.analysis.BaselineFitting(1)
get_baseline_polynome_analysis = dts.analyse(get_baseline_polynome_step)
polynome_coeffs1 = get_baseline_polynome_analysis.results["Fit_Coeffs"]

get_baseline_polynome_step = cwepr.analysis.BaselineFitting(3)
get_baseline_polynome_analysis = dts.analyse(get_baseline_polynome_step)
polynome_coeffs3 = get_baseline_polynome_analysis.results["Fit_Coeffs"]

plotter = cwepr.plotting.BaselineControlPlotter(dts.data, [polynome_coeffs0, polynome_coeffs1, polynome_coeffs3])
dts.plot(plotter)

correct_baseline_step = cwepr.processing.BaselineCorrection(polynome_coeffs1)
dts.process(correct_baseline_step)

phase_step = cwepr.processing.PhaseCorrection()
dts.process(phase_step)
