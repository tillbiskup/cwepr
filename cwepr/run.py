import os.path
import cwepr.dataset
import cwepr.analysis
import cwepr.processing
import cwepr.plotting
import cwepr.importers



path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

#Test-Spektrum 1
dts = cwepr.dataset.Dataset()
dts.import_from_file((path+"/Messdaten/1_No1-dunkel"))
dts.fill_axes()

dts_standard = cwepr.dataset.Dataset()
dts_standard.import_from_file((path+"/Messdaten/LiLiF-20180628"))
dts_standard.fill_axes()

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

plotter = cwepr.plotting.BaselineControlPlotter(dts.data.data, [polynome_coeffs0, polynome_coeffs1, polynome_coeffs3])
dts.plot(plotter)

correct_baseline_step = cwepr.processing.BaselineCorrection(polynome_coeffs1)
dts.process(correct_baseline_step)

phase_step = cwepr.processing.PhaseCorrection()
dts.process(phase_step)

plotter = cwepr.plotting.SimpleSpectrumPlotter()
dts.plot(plotter)

integrate_step1 = cwepr.analysis.IntegrationIndefinite()
integration = dts.analyse(integrate_step1)
integrate_values1 = integration.results["integral_values"]

integrate_step2 = cwepr.analysis.IntegrationIndefinite(y=integrate_values1)
integration = dts.analyse(integrate_step2)
integrate_values2 = integration.results["integral_values"]

verif = cwepr.analysis.IntegrationVerification(integrate_values1)
dts.analyse(verif)

final_integrate_step = cwepr.analysis.IntegrationDefinite(integrate_values1)
final_integrate = dts.analyse(final_integrate_step)
final_integral = final_integrate.results["integral"]
print(final_integral)

plotter = cwepr.plotting.SpectrumAndIntegralPlotter(integral_1=integrate_values1, integral_2=integrate_values2)
#dts.plot(plotter)

#Test Vergleich von Spektren

#Import Spectra
dts_v1 = cwepr.dataset.Dataset()
dts_v1.import_from_file((path+"/Messdaten/20190110-Daten-Dotierung/19_No1b-Sa483-dunkel-parallelB0"))
dts_v1.fill_axes()
dts_v2 = cwepr.dataset.Dataset()
dts_v2.import_from_file((path+"/Messdaten/20190110-Daten-Dotierung/20_No1b-Sa483-dunkel-senkrechtB0"))
dts_v2.fill_axes()

#Import Field Standard Spectrum
dts_vst = cwepr.dataset.Dataset()
dts_vst.import_from_file((path+"/Messdaten/20190110-Daten-Dotierung/LiLiF-20180628"))
dts_vst.fill_axes()

#Field Correction
nu_value = dts_vst.metadata.bridge.mw_frequency.value
get_B0_step = cwepr.analysis.FieldCorrectionValueFinding(nu_value)
get_B0_analysis = dts_vst.analyse(get_B0_step)
delta_b0 = get_B0_analysis.results["Delta_B0"]
correct = cwepr.processing.FieldCorrection(delta_b0)
dts_v1.process(correct)
dts_v2.process(correct)

#Frequency Correction
nu_target = dts_v1.metadata.bridge.mw_frequency
nu_given = dts_v2.metadata.bridge.mw_frequency
freq_correction_step = cwepr.processing.FrequencyCorrection(nu_given, nu_target)
dts_v2.process(freq_correction_step)

#Baseline Correction
get_baseline_polynome_step = cwepr.analysis.BaselineFitting(1)
get_baseline_polynome_analysis = dts_v1.analyse(get_baseline_polynome_step)
polynome_coeffs3 = get_baseline_polynome_analysis.results["Fit_Coeffs"]
correct_baseline_step = cwepr.processing.BaselineCorrection(polynome_coeffs1)
dts_v1.process(correct_baseline_step)

get_baseline_polynome_step = cwepr.analysis.BaselineFitting(1)
get_baseline_polynome_analysis = dts_v2.analyse(get_baseline_polynome_step)
polynome_coeffs1 = get_baseline_polynome_analysis.results["Fit_Coeffs"]
correct_baseline_step = cwepr.processing.BaselineCorrection(polynome_coeffs1)
dts_v2.process(correct_baseline_step)

#Integration
integrate_step1 = cwepr.analysis.IntegrationIndefinite()
integration = dts_v1.analyse(integrate_step1)
iv_v1 = integration.results["integral_values"]
final_integrate_step = cwepr.analysis.IntegrationDefinite(iv_v1)
final_integrate = dts_v1.analyse(final_integrate_step)
fi1 = final_integrate.results["integral"]

integrate_step1 = cwepr.analysis.IntegrationIndefinite()
integration = dts_v2.analyse(integrate_step1)
iv_v2 = integration.results["integral_values"]
final_integrate_step = cwepr.analysis.IntegrationDefinite(iv_v2)
final_integrate = dts_v2.analyse(final_integrate_step)
fi2 = final_integrate.results["integral"]

#Commonspace Check
cc_step = cwepr.analysis.CommonspaceAndDelimiters([dts_v1, dts_v2])
cd_check = dts_v1.analyse(cc_step)
delimiters = cd_check.results["delimiters"]
print(delimiters)

#Plot
multiplotter = cwepr.plotting.Multiplotter([dts_v1, dts_v2], integrals=[fi1, fi2])
multiplotter.plot()
#dts_v1.plot(multiplotter)


#Substract 2nd from 1st, then integrate + plot
subtract_step = cwepr.processing.SpectrumSubtract(dts_v1)
sub_values = dts_v2.process(subtract_step)

plotter_diff = cwepr.plotting.SimpleSpectrumPlotter()
#dts_v2.plot(plotter_diff)

integrate_step3 = cwepr.analysis.IntegrationIndefinite()
integration = dts_v2.analyse(integrate_step3)
integrate_values3 = integration.results["integral_values"]

integrate_step4 = cwepr.analysis.IntegrationIndefinite(y=integrate_values3)
integration = dts_v2.analyse(integrate_step4)
integrate_values4 = integration.results["integral_values"]

verif = cwepr.analysis.IntegrationVerification(integrate_values3)
dts_v2.analyse(verif)

final_integrate_step2 = cwepr.analysis.IntegrationDefinite(integrate_values3)
final_integrate2 = dts_v2.analyse(final_integrate_step2)
final_integral2 = final_integrate2.results["integral"]
print(final_integral2)

plotter2 = cwepr.plotting.SpectrumAndIntegralPlotter(integral_1=integrate_values3, integral_2=integrate_values4)
#dts_v2.plot(plotter2)

exporter = cwepr.importers.ExporterASCII()
exporter.export_from(dts_v2)
