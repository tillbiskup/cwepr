===============
Data processing
===============

Data processing is a necessary prerequisite for :doc:`data analysis <analysis>`, and therefore separate from the latter. The main effort in spectroscopy is usually *not* recording the raw data, but processing and analysing those data in order to answer the questions that triggered the measurements in the first place.

Processing steps can be categorised further. The following is an attempt to
do that for cwEPR data and to summarise how to properly record and
(post-)process cwEPR data. For more authoritative answers, you may as well have a look into the EPR literature, particularly the "EPR Primer" by Chechik/Carter/Murphy and the book on quantitative EPR by the Eatons.

Corrections
===========

When analysing cwEPR data, usually, a series of simple correction steps is
performed prior to any further analysis. This is particularly important if
you plan to compare different datasets or if you would like to compare your
spectra with those from the literature (always a good idea, though).

  * Magnetic field correction

    Usually, the magnetic field in an EPR measurement needs to be determined
    by measuring a field standard in the identical setup, as the actual
    magnetic field at the sample will usually differ from the field set in
    the software.

    Appropriate magnetic field correction becomes particularly important if
    you are interested in absolute *g* values of your sample, *e.g.* to
    compare it to literature data or quantum-chemical calculations and to
    get ideas as to where the unpaired spin may predominantly reside on (in
    terms of nuclear species).

  * Microwave frequency correction

    Comparing datasets is only possible in a meaningful manner if they are
    either corrected for same frequency, or their magnetic field axes
    converted in a g axis.

  * Microwave phase correction

    Usually, cwEPR spectra are not recorded with quadrature detection,
    *i.e.*, with both, absorptive and dispersive signal components. However,
    using the Hilbert transform, one can reconstruct the dispersive signal (
    imaginary component) and correct the phase of the microwave source this way.

  * Baseline correction

    However careful measurements are performed, baselines are quite often
    encountered. There are two different kinds of baseline that need to be
    corrected in different ways. Drifts of some kind can usually be handled
    by fitting and afterwards subtracting a (low-order) polynomial to the data.

    Particularly for low-temperature data, weak signals, and large magnetic
    field sweep ranges, resonator background can become quite dramatic.
    Here, usually the only viable way is to record the empty resonator
    independently under as much identical conditions as possible compared to
    recording the signal of the actual sample (but with slightly broader
    field range to compensate for different microwave frequency) and
    afterwards subtracting this dataset (empty resonator, *i.e.* resonator
    background signal) from the signal of the actual sample.


Algebra
=======

Comparing datasets often involves adding, subtracting, multiplying or
dividing the intensity values by a given fixed number. This is very simple
algebra and should probably be implemented in the ASpecD framework eventually.

Possible scenarios where one wants to multiply the intensity values of a
cwEPR spectrum may be comparing spectra resulting from a single species from
those of known two species, different (known) concentrations and alike.

Of course, dividing the intensity of the spectrum by the maximum intensity
is another option, however, this would be normalisation to maximum (not
always a good idea, usually normalising to area or amplitude is better),
and this is handled by a different set of processing steps (see below).

.. note::
    This type of simple algebra is quite *different* from adding or
    subtracting datasets together. Whereas simple algebra really is a
    one-liner in terms of implementation, handling different datasets
    involves ensuring commensurable axis dimensions and ranges, to say the
    least.


Normalisations
==============

Normalising data to some common characteristic is a prerequisite for
comparing datasets among each other.

There is a number of normalisations that are common for nearly every kind of
data, and as such, these normalisation steps should probably eventually be
implemented within the ASpecD framework. As there are:

  * Normalisation to maximum

    Simply divide the intensity values by their maximum

    Often used as a very simple "normalisation" approach. Depends highly on
    the situation and focus of the represenntation, but usually,
    other methods such as normalisation to amplitude or area, are better
    suited.

  * Normalisation to minimum

    Simply divide the intensity values by their minimum

    The same as for the normalisation to maximum applies here. Furthermore,
    normalising to the minumum usually only makes sense in case of
    prominent negative signal components, as in first-derivative spectra in
    cwEPR spectroscopy.

  * Normalisation to amplitude

    Divide the intensity values by the absolute of the difference between
    maximum and minimum intensity value

    Usually better suited as a simple normalisation than the naive
    normalising to maximum or minimum described above. However, it strongly
    depends on what you are interested in comparing and want to highlight.

  * Normalisation to area

    Divide the intensity values by the area under the curve of the spectrum

    Not as easy as it looks like for first-derivative cwEPR spectra,
    as here, you are usually interested in normalising to the same area (
    *i.e.*, integral of the curve) of the absorptive (zeroth-derivative or
    zeroth harmonic) spectrum.

    At least given appropriate measurement conditions (no saturation, no line
    bradening due to overmodulation, proper phasing), the cwEPR signal
    intensity should be proportional to the number of spins in the active
    volume of the resonator/probehead. Therefore, with all crucial
    experimental parameters directly affecting the signal strength being
    equal (microwave power, modulation amplitude), normalising to same area
    should be the most straight-forward way of comparing two spectra in a
    meaningful way.

    Bare in mind, however, that spectra with strongly different overall line
    width will have dramatically different minima and maxima, making
    comparison of this kind sometimes less meaningful.


Besides these rather general ways of normalising spectra (although described
above particularly with cwEPR data in mind), there are some other
normalisations more particular to cwEPR spectroscopy:

  * Normalisation to same number of scans

    Some spectrometers (probably only older ones) did usually sum the
    intensity for each scan, rather than afterwards dividing by the number
    of scans, making comparison of spectra with different number of scans
    quite tricky.

    Make sure you know exactly what you do before applying (or not applying)
    such normalisation if you would like to do some kind of (semi-)quantitative
    analysis of your data.

  * Normalisation to same receiver gain

    The preamplifiers in the signal channel (as the digitising unit in cwEPR
    spectrometers is usually called) have usually a gain that can be
    adjusted to the signal strength of the actual sample. Of course,
    this setting will have a direct impact on the intensity values recorded (
    usually something like mV).

    Comparing spectra recorded with different receiver gain settings
    therefore requires the user to *first* normalise the data to the same
    receiver gain setting. Otherwise, (semi-)quantiative comparision is not
    possible and will lead to wrong conclusions.

    Note on the side: Adjusting the receiver gain for each measurement is
    highly recommended, as setting it too high will make the signal clip and
    distort the signal shape, and setting it too low will result in data
    with (unnecessary) poor signal-to-noise ratio.


Handling 2D datasets
====================

2D datasets in cwEPR spectroscopy, huh? Well, yes, more often than one might
expect in the beginning. There are the usual suspects such as power sweeps
and modulation amplitude sweeps, each varying (automatically) one parameter
in a given range and record spectra for each value.

There are, however, other types of 2D datasets that are quite useful in
cwEPR spectroscopy. Some vendors of EPR spectrometers offer no simple way of
saving each individual scan in a series of accumulations. However, this may
sometimes be of interest, particularly as a single "spike" due to some
external event or other malfunctioning may otherwise ruin your entire
dataset, however long it might have taken to record it. Therefore, one way
around this limitations is to perform a 2D experiment with repeated field
scans, but saving each scan as a row in a 2D dataset.

Generally, there are at least two different processing steps of interest for
2D datasets:

  * Projection along one axis

    Equivalent to averaging along that axis

    If recording multiple scans of one and the same spectrum for better
    signal-to-noise ratio, but saving each scan individually within a row of
    a 2D dataset, this is the way to get the dataset with improved
    signal-to-noise ratio originally intended.

    May as well be used for rotation patterns, *i.e.*, angular-dependent
    measurements, if there turns out to be no angular dependence in the
    data. In this case, at least you save the measurement time by having a
    dataset with clearly better signal-to-noise ratio than initially intended.

  * Extraction of a slice along one dimension

    Having a 2D dataset, we may often be interested in only one slice along
    one dimension.

    Typical examples would be comparing two positions of the goniometer
    (zero and 180 degree would be an obvious choice) or slices with similar
    parameters for different datasets.


More complicated and probably more involved processing of 2D datasets would
be to (manually) inspect the individual scans and decide which of those to
average, *e.g.* in case of one problematic scan in between, be it due to
external noise sources or spectrometer problems.


Working with multiple datasets
==============================

Comparing multiple datasets by plotting them in one and the same axis is a
rather simple way of handling multiple datasets. However, usually, you would
like to perform much more advanced operations on multiple datasets, such as
adding and subtracting one from the other.

May sound pretty simple at first, but is indeed pretty demanding in terms of
its implementation, as internally, you need to check for quite a number of
things, such as commensurable axes and ranges. However, this is a rather
general problem of all kinds of datasets, hence it may be that this
functionality eventually gets incorporated in the ASpecD framework.

Particularly in EPR spectroscopy, each measurement will have a unique
microwave frequency for which the data were recorded. Therefore, to combine
the numerical values of two datasets (subtract, add, average), you will
first need to correct them for same microwave frequency. This will generally
result in different field axes for different datasets. Furthermore,
some vendors like to record data with non-equidistant field axes as well,
making handling of those datasets additionally messy.

  * Subtract a dataset from another dataset

    Ensure the datasets are compatible in terms of their axes (dimension,
    quantity, unit, common area of values), subtract the common range of
    values and return only the subtracted (*i.e.*, usually truncated) dataset.

    A common use case for subtracting a dataset from another would be a
    resonator background signal independently recorded, or some other
    background signal such as the "glass signal" (from impurities in the
    glass tube you've used).

    Other, more advanced applications may involve subtracting the spectrum
    of a single species from that of a spectrum consisting this and other
    species. However, in such case be aware of the fact that the spectrum
    containing more than one species may not be a simple superposition of
    the spectra of the two independent species.

  * Add a dataset to another dataset

    Ensure the datasets are compatible in terms of their axes (dimension,
    quantity, unit, common area of values), add the common range of values
    together and return only the summed (*i.e.*, usually truncated) dataset.

  * Average two datasets

    Ensure the datasets are compatible in terms of their axes (dimension,
    quantity, unit, common area of values), average the common range of values
    together and return only the averaged (*i.e.*, usually truncated) dataset.

    A common use case if you performed several independent measurements of
    the same sample (with otherwise similar/comparable parameters) and would
    like to average for better signal-to-noise.

