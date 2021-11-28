"""Module containing the analysis steps of the cwEPR package.

.. sidebar::
    processing *vs.* analysis

    For more details on the difference between processing and analysis,
    see the `ASpecD documentation <https://docs.aspecd.de/>`_.


An analysis step, in contrast to a processing step, does not simply modify a
given dataset, but extracts some characteristic of this dataset that is
contained in its ``results`` property. This can be as simple as a number,
*e.g.*, in case of the signal-to-noise figure of a data trace, but as
complicated as a (calculated) dataset on its own containing some measure as
function of some parameter, such as the microwave frequency for each of a
series of recordings, allowing to visualise drifts that may or may not
impact data analysis.


Note to developers
==================

Processing steps can be based on analysis steps, but not inverse! Otherwise,
we get cyclic dependencies what should obviously be avoided in order to keep
code working.

"""

import copy
import math
import numpy as np
import scipy.constants

import aspecd.analysis
import aspecd.dataset


class FieldCalibration(aspecd.analysis.SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """Determine offset value for a magnetic field calibration.

    While the microwave frequency of an EPR spectrometer can be measured with
    high accuracy independent of the resonator (and cryostat) used,
    the magnetic field values recorded are usually measured by a Hall probe
    or NMR teslameter away from the actual sample position. Hence,
    calibrating the recorded magnetic field value is necessary in case you
    are interested in quantitative *g*-value measurements or accurate
    comparisons between measurements.

    While spectrometers without removable probeheads (typically benchtop
    devices) come often calibrated by the manufacturer, in the typical research
    setup with probeheads and cryostats changing more frequent,
    field calibration is typically performed by the individual researcher
    recording the EPR spectrum of a standard sample with known *g* value.

    Correcting the magnetic field axis of a recorded EPR spectrum is in such
    cases actually a two-step process:

    #. Obtain the magnetic field offset value from the EPR spectrum of a
       field standard with known *g* value.

    #. Add the obtained value to the values of the magnetic field axis of the
       EPR spectrum that should be field-corrected.

    This class provides the first step, obtaining the magnetic field offset
    value for a number of well-known standards. And in case you use another
    field standard, you can simply provide the *g* value for this standard as
    well. The second step, correcting the magnetic field axis of your
    spectrum, is taken care of by the class
    :class:`cwepr.processing.FieldCorrection`. See the examples section
    below for further details.


    .. note::

        The method currently relies on the recorded spectrum of the field
        standard to consist of a single symmetric line accurately recorded
        with sufficient resolution. The *g* value


    Currently, the following field standards are supported:

    =========  =====  ===================  =========
    Substance  Name   *g* Value            Reference
    =========  =====  ===================  =========
    Li:LiF     LiLiF  2.002293 ± 0.000002     [1]
    DPPH       DPPH   2.0036 ± 0.0002         [2]
    =========  =====  ===================  =========

    References
    ----------
    [1] Stesmans and Van Gorp, *Rev. Sci. Instrum.* 60(1989):2949--2952.

    [2] Yordanov, *Appl. Magn. Reson.* 10(1996):339--350.

    The column "name" here refers to the value the parameter ``standard`` can
    take (see below). These names are case-insensitive.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        standard : :class:`str`
            Field standard that should be applied.

            For valid values, see the table above.

        g_value : :class:`float`
            *g* value of the standard sample.

            If you provide a standard by name using the ``standard``
            parameter above, this is not necessary. Providing a value here
            overrides the value for the standard. Hence use with care not to
            confuse you afterwards, when standard name and *g* value are
            inconsistent.

        mw_frequency : :class:`float`
            Microwave frequency to be corrected for.

            In general, this value is taken from the dataset and should
            therefore usually not be provided explicitly. Providing a value
            overrides reading from the dataset.

    Raises
    ------
    ValueError
        Raised if no microwave frequency or *g* value is available.


    See Also
    --------
    cwepr.processing.FieldCorrection :
        Correct magnetic field axis by a linear offset


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you have recorded the spectrum of a Li:LiF field standard and
    now you would like to obtain the field offset to correct your other
    spectra:

    .. code-block:: yaml

        - kind: singleanalysis
          type: FieldCalibration
          properties:
            parameters:
              standard: LiLiF
          result: deltaB0


    This result can now be used within the same recipe to perform a field
    correction of your other data. A more detailed example may look as follows:

    .. code-block:: yaml

        datasets:
          - /path/to/LiLiF/dataset
            label: lilif
          - /path/to/my/first/dataset
            label: first
          - /path/to/my/second/dataset
            label: second

        tasks:
          - kind: singleanalysis
            type: FieldCalibration
            properties:
              parameters:
                standard: LiLiF
            result: deltaB0
            apply_to: lilif

          - kind: processing
            type: FieldCorrection
            properties:
              parameters:
                offset: deltaB0
            apply_to:
              - first
              - second

    Here, we start by loading three datasets, a standard (LiLiF in this
    case) and two actual spectra. The first task is the analysis step to
    obtain the field offset value, performed only on the LiLiF spectrum,
    and the second is a processing step performed only on the two actual
    spectra to correct their field axis.

    Suppose you have used a standard that's currently not supported by name.
    Therefore, you will want to provide both, name and *g* value of the
    standard:

    .. code-block:: yaml

        - kind: singleanalysis
          type: FieldCalibration
          properties:
            parameters:
              standard: Strong pitch
              g_value: 2.0028
          result: deltaB

    Of course, providing the name of the standard does not change how the
    field offset is calculated, but it serves as documentation for you. Note
    that providing a *g* value overrides the value stored internally.
    Therefore, if you provide both, standard and *g* value, it is your sole
    responsibility to ensure consistency between those two parameters.

    .. versionchanged:: 0.2
        Renamed to FieldCalibration, added parameter ``g_value``

    """

    def __init__(self):
        super().__init__()
        self.parameters['standard'] = ''
        self.parameters['g_value'] = None
        self.parameters['mw_frequency'] = None
        self.description = "Determine magnetic field offset from standard"
        # NOTE: keys need to be all-lowercase
        self.g_values = {
            'dpph': 2.0036,
            'lilif': 2.002293,
        }

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Field calibration can only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def _sanitise_parameters(self):
        if not self.parameters['mw_frequency'] and not \
                self.dataset.metadata.bridge.mw_frequency.value:
            raise ValueError('No microwave frequency provided, aborting.')
        if not self.parameters['standard'] and not self.parameters['g_value']:
            raise ValueError('No standard or g value provided, aborting.')

    def _perform_task(self):
        self._assign_parameters()
        self.result = self._get_field_offset()

    def _assign_parameters(self):
        if not self.parameters['mw_frequency']:
            self.parameters['mw_frequency'] = \
                self.dataset.metadata.bridge.mw_frequency.value
        if not self.parameters['g_value']:
            self.parameters['g_value'] = \
                self.g_values[self.parameters['standard'].lower()]

    def _get_field_offset(self):
        """Calculates a field correction value.

        Finds the zero-crossing of a (derivative) spectrum of a field
        standard by using the difference between minimum and maximum part of the
        signal. This value is then subtracted from the the expected field
        value for the MW frequency provided.

        Returns
        -------
        delta_b0: :class:`float`
            Field offset to be added to magnetic field axis of dataset(s)

        """
        i_max = np.argmax(self.dataset.data.data)
        i_min = np.argmin(self.dataset.data.data)
        zero_crossing_exp = (self.dataset.data.axes[0].values[i_min] +
                             self.dataset.data.axes[0].values[i_max]) / 2
        calculated_field = \
            scipy.constants.value('Planck constant') \
            * self.parameters['mw_frequency'] * 1e9 * 1e3 / \
            (self.parameters['g_value']
             * scipy.constants.value('Bohr magneton'))
        delta_b0 = calculated_field - zero_crossing_exp
        return delta_b0


class LinewidthPeakToPeak(aspecd.analysis.SingleAnalysisStep):
    """Peak to peak linewidth in derivative spectrum.

    The linewidth is given in a first derivative spectrum as difference
    between the two extreme points. However, this is valid only for simple
    spectra with just one line or signal. This analysis step simply takes the
    difference on the magnetic field axis which is then stored in the result.
    The task can be used as follows:

    .. code-block:: yaml

      - kind: singleanalysis
        type: LinewidthPeakToPeak
        result: linewidth

    """

    def __init__(self):
        super().__init__()
        self.description = "Determine peak-to-peak linewidth"

    def _perform_task(self):
        self.result = self.get_peak_to_peak_linewidth()

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Line width detection can only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def get_peak_to_peak_linewidth(self):
        """Calculates the peak-to-peak linewidth.

        This is done by determining the distance between the maximum and the
        minimum in the derivative spectrum which should yield acceptable
        results in a symmetrical signal. Limitation: Spectrum contains only
        one line.

        Returns
        -------
        linewidth: :class:`float`
            peak to peak linewidth

        """
        index_max = np.argmax(self.dataset.data.data)
        index_min = np.argmin(self.dataset.data.data)
        linewidth = abs(self.dataset.data.axes[0].values[index_min] -
                        self.dataset.data.axes[0].values[index_max])
        return linewidth


class LinewidthFWHM(aspecd.analysis.SingleAnalysisStep):
    """Full linewidth at half maximum (FWHM).

    In EPR, this linewidth can be applied to integrated cwEPR spectra or
    spectra recorded in absorptive mode.
    The calculation is done by subtracting maximum/2, getting the absolute
    value and then determining the minima. The distance between these points
    corresponds to the FWHM linewidth.

    Examples
    --------
    Usage is quite simple as it requires no additional parameters:

    .. code-block:: yaml

        - kind: singleanalysis
          type: LinewidthFWHM
          result: linewidth


    """

    def __init__(self):
        super().__init__()
        self.description = "Determine linewidth (full width at half max; FWHM)"

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Line width detection can only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def _perform_task(self):
        self.result = self._get_fwhm_linewidth()

    def _get_fwhm_linewidth(self):
        """Calculates the line width (full width at half maximum, FWHM).

        Returns
        -------
        linewidth: :class:`float`
            line width as determined

        """
        index_max = np.argmax(self.dataset.data.data)
        spectral_data = copy.deepcopy(self.dataset.data.data)

        spectral_data -= max(spectral_data) / 2
        spectral_data = abs(spectral_data)

        left_zero_cross_index = np.argmin(spectral_data[:index_max])
        right_zero_cross_index = np.argmin(spectral_data[index_max:])
        b_field_left = self.dataset.data.axes[0].values[left_zero_cross_index]
        b_field_right = self.dataset.data.axes[0].values[right_zero_cross_index]
        return b_field_right - b_field_left


class SignalToNoiseRatio(aspecd.analysis.SingleAnalysisStep):
    """Get a spectrum's signal to noise ratio.

    This is done by comparing the absolute maximum of the spectrum to the
    maximum of the edge part of the spectrum (i.e. a part which is considered
    to not contain any signal.

    Attributes
    ----------
    parameters['percentage']: :class:`int`
        percentage of the spectrum to be considered edge part on any side
        (i.e. 10 % means 10 % on each side).

        Default: 10 %

    Examples
    --------
    The analysis can be applied either with or without the additional
    parameter "percentage":

    .. code-block:: yaml

        - kind: singleanalysis
          type: SignalToNoiseRatio
          properties:
            parameters:
                percentage: 7
          result: SNR

    """

    def __init__(self):
        super().__init__()
        self.parameters["percentage"] = 10
        self.description = "Determine signal to noise ratio."

    def _perform_task(self):
        """Determine signal to noise ratio.

        Call method to get the amplitude of the noise, compare it to the
        absolute amplitude and set a result.
        """
        signal = self.dataset.data.data
        noise = self._get_noise()

        noise_amplitude = self._get_amplitude(noise)
        signal_amplitude = self._get_amplitude(signal) - noise_amplitude

        self.result = signal_amplitude / noise_amplitude

    @staticmethod
    def _get_amplitude(data=None):
        return max(data) - min(data)

    def _get_noise(self):
        number_of_points = math.ceil(len(self.dataset.data.data) *
                                     self.parameters["percentage"] / 100.0)
        noise_data = np.append(self.dataset.data.data[:number_of_points],
                               self.dataset.data.data[-number_of_points:])
        return noise_data


class Amplitude(aspecd.analysis.SingleAnalysisStep):
    """Determine amplitude of dataset.

    Depending of the dimension of the dataset, the returned value is either
    a scalar (1D dataset) or a vector (2D dataset) containing the amplitude of
    each row respectively.

    Returns
    -------
    result
        amplitude(s) row-wise, thus scalar or vector.

    Examples
    --------
    The analysis is again called without additional parameters:

    .. code-block:: yaml

        - kind: singleanalysis
          type: Amplitude
          result: amplitude

    """

    def __init__(self):
        super().__init__()
        self.description = "Get amplitude of (derivative) spectrum."

    def _perform_task(self):
        if len(self.dataset.data.axes) == 2:
            self.result = max(self.dataset.data.data) - min(
                self.dataset.data.data)
        else:
            self.result = np.amax(self.dataset.data.data, axis=0) - np.amin(
                self.dataset.data.data, axis=0)


class AmplitudeVsPower(aspecd.analysis.SingleAnalysisStep):
    r"""Return a calculated dataset to further analyse a power-sweep experiment.

    The analysis of a power sweep results in a plot of the peak amplitude
    vs. the square root of the microwave power of the bridge. Both values
    are determined in this step and put together in a calculated dataset
    that can be used subsequently to perform the linear fit.

    Returns
    -------
    result: :class:`aspecd.dataset.CalculatedDataset`
       Calculated Dataset where the data is the amplitude and the axis
       values is the root of the mw-power (in ascending order).

    Examples
    --------
    For analysing a power sweep, extracting the amplitude and taking the root of
    the microwave power is the first step to success (see
    :ref:`power_sweep_analysis` for further details) and can be done as
    follows without additional parameters:

    .. code-block:: yaml

        - kind: singleanalysis
          type: AmplitudeVsPower
          result: power_sweep_analysis

    A more complete example of a power sweep analysis including linear fit
    of the first *n* points and a graphical representation of the results may
    look as follows:

    .. code-block:: yaml

        datasets:
          - PowerSweep
        tasks:
          - kind: singleanalysis
            type: AmplitudeVsPower
            apply_to:
              - PowerSweep
            result: power_sweep_analysis
          - kind: singleanalysis
            type: PolynomialFitOnData
            properties:
              parameters:
                order: 1
                points: 5
                return_type: dataset
            apply_to:
              - power_sweep_analysis
            result: fit
          - kind: multiplot
            type: PowerSweepAnalysisPlotter
            properties:
              properties:
                drawings:
                  - marker: '*'
                  - color: red
                grid:
                  show: true
                  axis: both
                axes:
                  ylabel: '$EPR\\ amplitude$'
              filename: powersweepanalysis.pdf
            apply_to:
              - power_sweep_analysis
              - fit


    This would result in a power saturation curve (EPR signal amplitude as a
    function of the square root of the microwave power, the latter usually
    in mW), and a linear fit covering in this case the first five data points.

    """

    def __init__(self):
        super().__init__()
        self.description = "Return calculated dataset for power sweep analysis."
        self.result = aspecd.dataset.CalculatedDataset()
        # private properties
        self._analysis = None
        self._roots_of_mw_power = np.ndarray([])

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Extracting the EPR signal amplitude as function of the microwave
        power can only be applied to 2D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return len(dataset.data.axes) == 3

    def _perform_task(self):
        self._calculate_data_and_axis()
        self._check_mw_axis()
        self._assign_data_to_result()
        self._assign_units_to_result()

    def _calculate_data_and_axis(self):
        self._roots_of_mw_power = np.sqrt(self.dataset.data.axes[1].values)
        amplitude = Amplitude()
        self._analysis = self.dataset.analyse(amplitude)

    def _check_mw_axis(self):
        """Check for ascending order.

        If not, revert both, root of mw-power and amplitude.
        """
        if self._roots_of_mw_power[-1] - self._roots_of_mw_power[0] < 0:
            self._roots_of_mw_power = self._roots_of_mw_power[::-1]
            self._analysis.result = self._analysis.result[::-1]

    def _assign_data_to_result(self):
        self.result.data.data = self._analysis.result
        self.result.data.axes[0].values = self._roots_of_mw_power

    def _assign_units_to_result(self):
        if self.dataset.data.axes[1].unit == 'mW':
            self.result.data.axes[0].unit = 'sqrt(mW)'
        elif self.dataset.data.axes[1].unit == 'W':
            self.result.data.axes[0].unit = 'sqrt(W)'
        self.result.data.axes[0].quantity = 'square root of mw power'
        self.result.data.axes[1].quantity = 'EPR amplitude'


class PolynomialFitOnData(aspecd.analysis.SingleAnalysisStep):
    """Perform polynomial fit on data and return its parameters or a dataset.

    Developed tests first.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        points
            first n points that should taken into account

            Default: 3

        order
            order of the fit.

            Default: 1

        return_type : :class: `str`
            Choose to returning the coefficients of the fit or a calculated
            dataset containing the curve to plot.

            Default: coefficients.

            Valid values: 'coefficients', 'dataset'

        add_origin : :class: `bool`
            Adds the point (0,0) to the data and axes, but  does not guarantee
            the fit really passes the origin.

            Default: False.

    Examples
    --------
    Some Parameters can be chosen here, depending on the purpose and the
    following analysis and processing steps.

    .. code-block:: yaml

        - kind: singleanalysis
          type: PolynomialFitOnData
          properties:
            parameters:
                points: 5
                order: 2
                return_type: dataset
                add_origin: True
          result: fit

    """

    def __init__(self):
        super().__init__()
        self.description = "Perform polynomial fit and return parameters."
        self.result = None
        self.parameters['points'] = 3
        self.parameters['order'] = 1
        self.parameters['return_type'] = 'coefficients'
        self.parameters['add_origin'] = False
        self.parameters['coefficients'] = []
        # private properties
        self._curve = None

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Polynomial fitting can only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def _perform_task(self):
        if self.parameters['add_origin']:
            self._add_origin()
        self._get_coefficients()
        self._get_curve()
        self._assign_result()

    def _get_coefficients(self):
        x_data_to_process = \
            self.dataset.data.axes[0].values[:self.parameters['points']]
        y_data_to_process = self.dataset.data.data[:self.parameters['points']]
        self.parameters['coefficients'] = \
            np.polyfit(x_data_to_process, y_data_to_process, self.parameters[
                'order'])

    def _get_curve(self):
        self._curve = self.create_dataset()
        self._curve.data.axes[0] = self.dataset.data.axes[0]
        self._curve.data.data = np.polyval(self.parameters['coefficients'],
                                           self.dataset.data.axes[0].values)
        self._curve.data.axes[0].values = self.dataset.data.axes[0].values

    def _assign_result(self):
        if self.parameters['return_type'].lower() == 'dataset':
            self.result = self._curve
        else:
            self.result = self.parameters['coefficients']

    def _add_origin(self):
        self.dataset.data.axes[0].values = \
            np.insert(self.dataset.data.axes[0].values, 0, 0)
        self.dataset.data.data = np.insert(self.dataset.data.data, 0, 0)


class PtpVsModAmp(aspecd.analysis.SingleAnalysisStep):
    """Create calculated dataset for modulation sweep analysis.

    For a modulation sweep analysis, the first step is to get the peak to
    peak amplitude and correlate it to the modulation amplitude,
    see :ref:`modulation_sweep_analysis` for further details.

    Examples
    --------
    The usage is also quite simple without additional parameters necessary:

    .. code-block:: yaml

        - kind: singleanalysis
          type: PtpVsModAmp
          result: calc_dataset

    """

    def __init__(self):
        super().__init__()
        self.description = 'Create dataset with ptp-linewidth vs modulation ' \
                           'Amplitude.'
        self.result = aspecd.dataset.CalculatedDataset()
        self.linewidths = np.ndarray([])

    def _perform_task(self):
        self._get_linewidths()
        self._fill_dataset()

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Extracting the peak-to-peak linewidth as function of the modulation
        amplitude can only be applied to 2D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return len(dataset.data.axes) == 3

    def _get_linewidths(self):
        index_max = np.argmax(self.dataset.data.data, axis=0)
        index_min = np.argmin(self.dataset.data.data, axis=0)
        self.linewidths = self.dataset.data.axes[0].values[index_min] \
            - self.dataset.data.axes[0].values[index_max]

    def _fill_dataset(self):
        self.result.data.data = self.linewidths
        self.result.data.axes[0] = self.dataset.data.axes[1]
        self.result.data.axes[1].unit = self.dataset.data.axes[0].unit
        self.result.data.axes[1].quantity = 'peak to peak linewidth'


class AreaUnderCurve(aspecd.analysis.SingleAnalysisStep):
    """Make definite integration, i.e. calculate the area under the curve.

    Takes no other parameters and returns a single number. However, this step
    does not (yet) account for baselines or noise thus that the value
    obtained here is to be taken with care.

    Examples
    --------
    .. code-block:: yaml

        - kind: singleanalysis
          type: AreaUnderCurve
          result: area

    """

    def __init__(self):
        super().__init__()
        self.description = "Definite integration / area und the curve"

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Calculating the area can only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def _perform_task(self):
        x_values = self.dataset.data.axes[0].values
        y_values = self.dataset.data.data

        self.result = np.trapz(y_values, x_values)
