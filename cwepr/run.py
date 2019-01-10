import os.path
import cwepr.dataset
import cwepr.analysis
import cwepr.processing
import cwepr.plotting


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

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
dts.plot(plotter)


