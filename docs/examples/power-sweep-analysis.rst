=========================
Power saturation analysis
=========================

A crucial step when recording cw-EPR spectra is to optimise the microwave power and to prevent saturation from distorting the signal shape. Therefore, usually a power saturation analysis is conducted, *i.e.* recording a series of spectra with systematically varying the microwave power.

From the resulting data, the EPR signal amplitude is extracted and plotted as function of the square root of the microwave power. As long as no saturation is occurring, there should be a linear dependency between signal amplitude and square root of microwave power. To further help with analysis, a linear regression covering the first *n* points can be performed and the results plotted together with the power saturation curve on one figure.


.. literalinclude:: ../../examples/power-sweep-analysis/power-sweep-analysis.yaml
    :language: yaml
    :linenos:
    :caption: Complete recipe for a power saturation analysis, including plotting the results.
