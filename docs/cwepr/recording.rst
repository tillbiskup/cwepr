========================
Recording cw-EPR spectra
========================

What is the usual way of recording cw-EPR spectra of an unknown sample?

To obtain data that can be properly post-processed and analysed, the signal should not be distorted by either saturation or overmodulation, and it should be as good as possible in terms of its signal-to-noise ratio.

Furthermore, if you would like to compare spectra among each other, you will need to ensure that you calibrate your field, usually by recording the spectrum of a sample with known *g* factor (commonly referred to as "field standard") or have it properly calibrated (*e.g.*, once by a technician upon setting up the spectrometer in your lab).


.. note::
    Basic familiarity with operating an EPR spectrometer is tacitly assumed. You will find no information how to couple your resonator and similar things, as this strongly depends on the setup you're using.


Field range
===========

How to know over which field range to sweep? The answer strongly depends on the kind of sample you're measuring. Organic radicals usually show rather narrow signals of 5-10 mT centred about a *g* value of *g* = 2. Metals are a completely different thing. They have often quite broad spectra and can easily have g values in the range of 1.9-4 and beyond.

In any case, make sure to record enough "baseline" left and right of your actual signal. Beware of your signal having Lorentzian shape. In this case, you will have very broad "wings" with very little intensity, hence need to record quite a bit of "baseline" not to truncate your spectrum. Furthermore, if you plan to correct the phase of your spectra afterwards, having the spectra recorded rather broad is particularly important, as the dispersive component is quite broad as well.

From own experience, people usually tend to record data over a far too narrow field range.


Microwave power: power sweep
============================

What microwave power to use? Obviously, more is not always better, as you may easily saturate your signals, resulting in broadening that you cannot easily correct for afterwards. Besides that, it strongly depends on your setup what microwave power will yield reasonable results.

The only way to really know what setting to use to not distort your signal shape is to perform a series of measurements with different microwave power settings. This is colloquially known as "power sweep".

As 3 dB change in attenuation translates to a factor of 2 in microwave power, 3-dB steps for a power sweep are quite common.

How such power sweep is analysed will be described in more detail later. For now just one important comment:

.. warning::
    Saturation sets in *much before* your signal amplitude decreases again. Often you will not reach the point where you oversaturate your signal so much that its intensity decreases again.


The only valid way of determining whether you are not (yet) saturating is to record two spectra with different microwave power and make sure the intensity difference translates to the same factor as the power difference. Hence, if you record two spectra with 3 dB attenuation difference, your spectra should have an intensity ratio difference of 2, the one recorded with 3 dB less attenuation being twice as large as the other one. Beware that with "intensity", we mean the area under the curve, *i.e.* the double integral of the first-derivative spectrum usually obtained in cw-EPR spectroscopy (due to the lock-in detection scheme).

Important aspects to consider when setting up the parameters for a power sweep: As you change the microwave power incident at your sample, your signal size will vary dramatically as well. This will affect other settings, mostly the receiver gain (more on that below), but you will need to take into account that for low power, your signal-to-noise ratio might dramatically reduce as well. Therefore, better try to quickly run a single spectrum at the lowest power setting you have in mind for your power sweep range to see how many accumulations you would need to get a sensible signal-to-noise ratio that allows you to analyse your data.


Modulation amplitude: modulation-amplitude sweep
================================================

Next question when recording cw-EPR spectra: What value for the modulation amplitude shall I choose in order *not* to distort my signal? The seminal answer to this question would be something in line of: Choose the modulation amplitude to be a factor of two (to ten) smaller than your actual line width.

Congratulations. How to know what line width to expect of your signal before you managed to record a distortion-free spectrum? The approach is quite similar to the one for choosing the correct microwave power (see above for details on that). You record a series of spectra with systematically varying the modulation amplitude, colloquially known as "modulation-amplitude sweep".

The value of choice is the largest modulation amplitude that doesn't change the signal shape any more. Of course, this is only a valid  judgement if your signal-to-noise ratio is high enough to be certain that there really is no effect any more, not that you're not only not seeing any effect due to too much noise.


.. warning::
    The modulation amplitude for a given resonator needs to be calibrated, typically using a standard sample with a very narrow line. Therefore, make sure you've loaded and applied the correct calibration file corresponding to the resonator you're using. Besides that, be aware that due to miscalibration or missing calibration, modulation amplitude settings may not be easily transferred between setups. Technically speaking, they should be comparable if everything was properly calibrated. Reality has it that your setup is not always properly calibrated (and that you sometimes simply forget to check for the correct calibration file to be loaded).


How to automatically analyse such a modulation-amplitude sweep will be detailed later. But if you're looking for a "quick and dirty" approach, here it is: Record two spectra with different modulation amplitude and plot them scaled to same signal amplitude. If you see no difference in spectral shape, you can be rather sure that you are not overmodulating your signal. If you were already overmodulating, your line width would be a function of the modulation amplitude applied, hence vary with the spectrometer setting.

A word of caution for this type of often automatically performed measurements: The setting of the modulation amplitude will directly and dramatically impact your overall signal strength, with signals being much larger with larger modulation amplitude. Hence, make sure with a short series of scans using the minimum and maximum modulation amplitude setting that you are not clipping your detector (receiver gain setting, see below) and that you still get signals with meaningful signal-to-noise ratio for analysis when recording with the smallest modulation amplitude.


Receiver gain
=============

The amplification of the preamplifier in the signal path of your cw-EPR spectrometer can usually be controlled. Typically, the amplification (gain) setting is given in dB values, as the available range spans several orders of magnitude (60-90 dB are a typical range).

Why does the receiver gain setting matter at all? Two reasons: If you set the gain to a value too high, your signal will be amplified by more than what your detector can handle. Hence, you're clipping your signal and therefore distorting it. If you really overdo this, you will get a flat horizontal line. Much more tricky are those cases where you still overload your detector, but it will respond with a somewhat "smooth" curve that is nevertheless distorted. Usually, one only finds out in retrospect by trying to simulate the data. Sometimes, if you know what you expect, you can judge from the spectral shape that there is some distortion from a too high gain setting.

The opposite end is a receiver gain setting that is too low. The receiver gain, hence signal amplification, has a strong impact on the signal-to-noise figure of your recorded signal. Of course, you're interested in obtaining the best signal-to-noise ratio, often in the shortest possible time. Therefore, set your receiver gain such that the range the detector covers is not much more than 20 percent larger than your signal. Often spectrometer control software nowadays allows to preview the gain setting.


Signal channel settings
=======================

Depending on the type of setup you use, you will usually have to deal with two parameters: conversion time and time constant.

The conversion time is the time the digitizer in the signal channel spends on acquiring signal on every magnetic field point, and is therefore directly connected to the total sweep time for one scan and the number of field points to record. Generally, the longer you set your conversion time, the better your signal-to-noise ratio will become. However, this has some intrinsic limitations. One is the overall stability of your setup that might make it favourable to use shorter conversion times and more individual scans. Another is the lifetime of the paramagnetic species you are interested in. If you are measuring transient species with a limited lifetime, your conversion time should be short compared to the signal change, and if you would like to not only record the signal change on a single magnetic field position, but acquire complete spectra, it should even be much shorter, at least by the factor of field points you record for a single spectrum.

The time constant, on the other hand, acts as a filter to reduce the noise on the acquired signal. Therefore, larger time constants will generally lead to less noisy spectra. However, this filtering comes to a price, and you need to ensure not to accidentially filter your signal and hence distort its line shape. Usually, you will find advice in the literature to set the time constant at least a factor of four smaller than the conversion time, and at least a factor of ten smaller than it takes to pass through the narrowest line of your spectrum. In any case, the value for the time constant should be *smaller* than that of the conversion time. If in doubt, your best bet will usually be to try it out using a sample with decent signal strength, and make sure the signal shape does not change at all when increasing the time constant, at least not beyond available spectrometer accuracy and repeatability.


Digital filters
===============

Modern spectrometers come equipped with digital signal processing capabilities that are often switched on by default. While generally, there is nothing wrong with digital signal processing, and the EPR community can probably learn a lot from the concepts developed in this (engineering) field decades ago and applied in probably more devices we're using daily than we can imagine, scientists should usually strive for signals that are as much unprocessed as possible.

Discussing what the term "raw data" actually means would be out of scope of this introduction. But it should be immediately obvious that if we can choose between automatic filtering and no automatic filtering, we should probably opt for the latter, particularly if there is no other way to get the raw, unprocessed data out of the spectrometer software.

Filtering is a very powerful tool, and it has its use in preprocessing of data for complex analyses, such as fitting, finding peaks, etcetera. However, it should never be used to make spectra appear less noisy and hence more pleasant to the eye. This is simply unscientific and should never be done. If there is good reasons to "denoise" your data, clearly state why and what you have done.


Number of field points
======================

How many field points should I record? The simple answer would be something in line of: Enough points to sample even the highest frequency in your spectrum appropriately. But what does that mean?

In old days, there were pretty distinct settings for the number of field points to record with cw-EPR spectrometers. Due to hardware limitations, you could only record powers of two, usually starting with 512 and ending with 8192 points. This simply corresponded to the available memory of your digitizer. A useful side effect of this is that if you would like to apply a Fourier transform to your data (why you would want to do those strange things is a topic for later), you would anyways better make your data points be a power of two.

Back to topic. A somewhat sensible setting would be to record ten data points per modulation amplitude. This appears to be a standard setting on Bruker cw-EPR spectrometers nowadays, and for good reason. The underlying assumption: Your modulation amplitude should be smaller than the smallest line width in your spectrum, and ten data points will be sufficient to faithfully reproduce a periodic signal with a frequency corresponding in its period to that field range.

Generally, as nowadays memory is no real limitation any more, it is always a good advice to record *more* points than you would usually need, as thus, you sample your noise frequencies with quite some accuracy, rendering it much easier to discriminate between noise and (sharp) signal afterwards by means of Fourier transform or wavelet analysis.


Recording each scan independently
=================================

Usually, you will need to record more than one scan to obtain a sufficient signal-to-noise ratio of your signal. The exception proves the rule.

One problem with recording multiple scans can be that many spectrometers average the scans immediately, not saving the individual scans. This is fine as long as everything goes smooth. However, having personal experience with an environment where you frequently obtain random noise from unknown sources resulting in narrow spikes in your spectra, we strongly recommend saving each scan individually wherever possible.

Some spectrometers do this *per se*, with others, such as Bruker spectrometers, you can usually perform "field delay" measurements and set the delay to a very short time. A "field delay" measurement is kind of a kinetic experiment where you repeatedly perform a convential field sweep experiment and save the results as individual rows of a two-dimensional dataset. In this case, all information regarding other parameters of the setup, such as the microwave frequency, that may change during the measurement, are nevertheless lost.

Of course, having recorded 2D datasets instead of the usual 1D datasets makes it less convenient to look at the data, as you first need to average over the second dimension. However, given a software package like cwepr, this can pretty easily be dealt with.
