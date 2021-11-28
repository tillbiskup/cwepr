=============
Data analysis
=============

In nearly all cases, data analysis needs to be preceded with :doc:`data processing <processing>`. While processing steps can usually be automated to a large extend and are rather generally applicable, data analysis is usually much more focussed on individual types of measurements and the actual questions at hand.

Eventually, fitting spectral simulations to the recorded data can be regarded as analysis steps as well. Usually, they are the only way to extract parameters from cw-EPR data with sufficient accuracy. However, this is not and will never be the realm of the cwepr package, but that of dedicated packages.

Nevertheless, there are a number of analysis steps that are rather generic, particularly regarding routine measurements necessary to find the appropriate experimental settings for :doc:`recording accurate cw-EPR spectra <recording>`, namely power and modulation sweeps.

.. _power_sweep_analysis:

Power sweep analysis
====================

  * For spectra consisting of a single (dominating) line, this is rather straight-forward.
  * For spectra consisting of several overlapping species or several lines, it may become much more involved.

While generally, finding the maximum of an (integrated) spectrum sounds not to be too complicated, for noisy traces this becomes usually quite error-prone. If only interested in the maximum intensity, not the position on the field axis, an approach would be to subtract half the noise amplitude determined at the left and/or right end of the spectrum. Beware that for power sweeps, usually the spectra get quite noisy for low microwave power settings.

Besides finding the maximum microwave power level for distortion-free recording of cw-EPR spectra, comparing the saturation behaviour of different samples recorded under identical or at least comparable experimental conditions (same spectrometer, same resonator/probehead, same solvent, same temperature or at least physical condition) can give hints on different spin multiplicity or spin-spin interactions. Generally, both, a higher spin multiplicity and spin-spin interactions will result in shorter relaxation times, translating to saturation at higher microwave power levels.

.. important::

    As mentioned already when discussing how to :doc:`record cw-EPR spectra <recording>`, the maximum microwave power level possible before saturating the signal usually needs to be determined for each sample individually. For one and the same type of samples measured at the same setup with comparable physical condition, a power sweep may, however, be performed only once. Nevertheless, keep in mind that those settings can usually *not* be transferred between different setups.

.. _modulation_sweep_analysis:

Modulation sweep analysis
=========================

 * For a single line, this is rather straight-forward, "simply" plotting the peak-to-peak line widths versus the modulation amplitude.
 * For spectra consisting of many narrow lines, it would require to either narrow the range of the recorded spectra to a single line, or involving peak-finding algorithms.

Similarly to the discussion above for the power sweep analysis, finding the extrema of a spectrum sounds not too complicated for starters. However, for analysing modulation sweeps, we are interested in the field position of these extrema, not in their intensity values. Therefore, the noisier the data get, the more involved it gets to accurately determine the field positions.


Rotation pattern analysis
=========================

Analysing rotation patterns, *i.e.* angular-dependent recording of cw-EPR spectra, can become quite complex and involved. However, there are a few things that can always be checked for, helping to determine accurate data recording.

Due to general physical considerations, the EPR spectra recorded for 0 and 180° of a sample should always be identical within experimental error. To be exact, any two positions with 180° (or *n* pi) angular difference between should result in identical EPR spectra. Therefore, a standard analysis of rotation patterns is to plot those two traces on top of each other. Ideally, they should be identical both in terms of their spectral shape and intensity. Differences in spectral shape are usually a good hint for the rotation not being accurate. From own experience, even if the sample tube was turned accurately, that does not necessarily guarantee the sample to have followed this rotation equally well. In particular, flat substrates that are not physically locked within the tube tend to move during rotating the tube.


Comparing cw-EPR spectra
========================

What is normally considered a simple task, comparing two or more recorded cw-EPR spectra, is much more tricky than one might think at first. Of course, the procedure taken depends dramatically on the ultimate goal of comparing as well. If you would like to do a semi-quantitative comparison of a series of spectra, you need to take different things into account as if you are interested in comparing spectral shapes.


Semi-quantiative analysis
-------------------------

Suppose you have recorded a series of cw-EPR spectra of different samples and would like to compare them in a semi-quantitative way, *i.e.* only with respect to their relative intensities. Note that this is different from spin quantification. For details of the latter, see below.

There are a number of experimental parameters that influence the signal intensity as recorded by your spectrometer, and that need to be known for any meaningful comparison:

  * Microwave power
  * Modulation amplitude
  * Receiver gain
  * Time constant/conversion time
  * Q value

While you can numerically account for microwave power, receiver gain, and Q value, the other parameters better be set identical during recording. And of course, microwave power and receiver gain need to be in a range that does not saturate your signal or clip the detector, respectively.

The absolute intensity values are usually arbitrary units and thus not comparable at all between different setups. The same is true for different resonators within the same spectrometer. Positioning of the resonator between the pole tips of your magnet influences the signal intensity as well, although probably to a smaller extent. Measuring with and without cryostat, however, will certainly make a more dramatic difference.

Suppose you have recorded all samples with identical experimental settings, and you are reasonably confident that the resulting spectra are neither saturated nor over-modulated nor clipped nor otherwise distorted. If you forgot to record the Q value, you cannot reliably do a semi-quantiative analysis, at least not if you would like to do better than an order-of-magnitude estimation.

If all requirements are reasonably fulfilled, the next step is to doubly integrate your spectra recorded with the usual lock-in detection scheme. Sounds simple, is mathematically well-defined, but in reality often rather tricky. These steps usually need to be carried out:

  * Baseline correction (at least 0th order)
  * 1st integration
  * Visual inspection of the resulting absorptive spectrum
  * Baseline correction (1st order)
  * 2nd integration (resulting in a number)

The first baseline correction is necessary to have begin and end of your spectrum being (very) close to zero, as otherwise your result will have some offset. Visually inspecting the result of the first integration is highly important, as you may not have recorded a sufficient magnetic field range, resulting in your absorptive spectrum to be distorted. Be aware of the Lorentzian contribution to the line shape that has really broad wings in the absorptive spectrum basically invisible in the first-derivative shaped lock-in detected cw-EPR spectrum. Usually, a second baseline correction is necessary for experimental data, as the first integration results in the absorptive spectrum to deviate from zero on its right end. If this second baseline correction is successful, you may trust your final quantification.

.. note::

    An easy way to check how accurate your measurements can be, simply record a series of spectra of the identical sample, but not simply by pressing the "run" button of your spectrometer control software again and again. Rather, remove and reinsert your sample after each measurement, as this gives you an immediate feedback of how accurate you can reposition your sample. If you compare spectra of different samples, this is an unavoidable source of errors and deviations.


Comparing spectral shapes
-------------------------

When starting to compare spectral shapes, the first thing you should always do is to correct the spectra for the same microwave frequency. As long as you have recorded all spectra with the identical setup and *not* changed the resonator in between, you may be safe with simply applying the resonance condition of magnetic resonance for this purpose. If, however, you would like to compare spectra recorded with different setups, either you can be reasonably confident that each setup has a calibrated magnetic field, or you have recorded a field standard straight before or after recording your actual data. In the latter case, additionally to the frequency correction, you would need to perform a magnetic field correction as well using the spectrum recorded for the field standard, usually a sample with a very narrow (and isotropic, *i.e.* symmetric) line and an accurately known *g* value.

But now for comparing spectral shapes. Probably there is no one "true" or "correct" solution for displaying spectra to compare their shape. Rather, your representation of choice may depend on what you would like to highlight. Usually, if you are interested in different spectral shapes, you would like to normalise the spectra in some way or other. Possibilities for normalisation would be:

  * Peak-to-peak amplitude
  * Maximum
  * Minimum
  * Area under curve

    (Note: For first-derivative spectra, the area under the curve is *not* identical to the number of spins contributing to the signal!)

You should, however, never simply plot the spectra "as is" and start interpreting some overlapping parts in some way. This would mean that you implicitly perform a semi-quantitative analysis, and this is in this way most certainly wrong. For details why this is the case and how to do better, see above.


Spin quantification
===================

Quantitative EPR is a field on its own. There is an excellent book on the topic authored by the Eatons that is highly recommended for everybody interested in performing quantitative EPR of any kind (not only spin quantification, but as well accurate measurements of *g* values).

If you happen to have access to a calibrated commercial spectrometer, spin counting of samples at room temperature that consist of only one species may be quite straight-forward, given that you managed to record your data accurately, with minimum phase error and baseline. The latter points are highly important, as spin counting involves integrating the spectra. If all these conditions are met, it may be as simple as running some built-in routine of the measurement control software.

However, generally, you should take results from spin counting with a grain of salt. Order-of-magnitude estimation is usually pretty fair, but interpreting differences of a factor of two in terms of absolute numbers and comparing those measurements with other methods of counting spins require very high precision and great care in data acquisition.

