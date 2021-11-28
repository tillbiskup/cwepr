"""Metadata: Information on numeric data stored in a structured way.

Metadata
========

In this module, the individual metadata classes are defined which contain the
metadata for the different types of datasets:

  * :class:`cwepr.metadata.ExperimentalDatasetMetadata`
  * :class:`cwepr.metadata.CalculatedDatasetMetadata`

What may sound like a minor detail is one key aspect of the cwepr package:
The metadata and their structure provide a unified interface for all
functionality operating on datasets. Furthermore, the metadata contained
particularly in the :class:`cwepr.metadata.ExperimentalDatasetMetadata` class
are the result of several years of practical experience. Reproducible research
is only possible if all information necessary is always recorded, and this
starts with all the metadata accompanying a measurement. Defining what kind
of metadata is important and needs to be recorded, together with metadata
formats easily writable by the experimenters *during* recording the data
requires a thorough understanding of both, the method and the setup(s) used.
For an overview of the structures of the dataset classes and their
corresponding metadata, see the :doc:`dataset structure </dataset-structure>`
section.


Module documentation
====================

"""
import aspecd.metadata
import aspecd.utils

from cwepr.exceptions import UnequalUnitsError


class ExperimentalDatasetMetadata(aspecd.metadata.ExperimentalDatasetMetadata):
    """Set of all metadata for a dataset object.

    Metadata as a unified structure of information coupled to the dataset are
    necessary for the understanding, analysis and processing of data,
    especially in cwepr. Too many parameters have an direct influence to the
    spectral shape of the spectrum that anything other than saving them in an
    appropriate place and accessing them automatised in the respective tasks
    is no option. Some parameters are written automatically by the
    spectrometer's software, others, depending also on the actual setup (that
    may change over time!) are omitted and it is highly recommended those
    should be noted by hand, for example in an *.info-file.*

    Attributes
    ----------
    measurement: :class:`cwepr.metadata.Measurement`
        Metadata corresponding to the measurement.

    sample : :class:`cwepr.metadata.Sample`
        Metadata corresponding to the sample.

    temperature_control : :class:`cwepr.metadata.TemperatureControl`
        Metadata corresponding to the temperature.

    experiment: :class:`cwepr.metadata.Experiment`
        Metadata corresponding to the experiment.

    spectrometer: :class:`cwepr.metadata.Spectrometer`
        Metadata corresponding to the spectrometer.

    magnetic_field: :class:`cwepr.metadata.MagneticField`
        Metadata corresponding to the magnetic field.

    bridge: :class:`cwepr.metadata.Bridge`
        Metadata corresponding to the microwave bridge.

    signal_channel: :class:`cwepr.metadata.SignalChannel`
        Metadata corresponding to signal channel.

    probehead: :class:`cwepr.metadata.Probehead`
        Metadata corresponding to the probehead used for the experiment.

    metadata_modifications : :class:`list`
        List of all modifications performed on the metadata, e.g, overrides.

    """

    def __init__(self):
        super().__init__()
        self.measurement = Measurement()
        self.experiment = Experiment()
        self.sample = Sample()
        self.spectrometer = Spectrometer()
        self.magnetic_field = MagneticField()
        self.bridge = Bridge()
        self.signal_channel = SignalChannel()
        self.probehead = Probehead()
        self.temperature_control = TemperatureControl()
        self.metadata_modifications = []


class CalculatedDatasetMetadata(aspecd.metadata.CalculatedDatasetMetadata):
    """Metadata for a calculated dataset.

    This class contains the minimal set of metadata for a dataset consisting
    of calculated data, i.e., :class:`cwepr.dataset.CalculatedDataset`.

    Metadata of actual datasets should extend this class by adding
    properties that are themselves classes inheriting from
    :class:`aspecd.metadata.Metadata`.

    Metadata can be converted to dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`, e.g., for generating
    reports using templates and template engines.
    """


class Measurement(aspecd.metadata.Measurement):
    """Metadata corresponding to the measurement.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing properties to set.

    Attributes
    ----------
    label: :class:`str`
        Label of the sample, including the sample-number.

    """

    def __init__(self, dict_=None):
        # public properties
        self.label = ''
        super().__init__(dict_=dict_)


class Sample(aspecd.metadata.Sample):
    """Metadata corresponding to the sample .

    As this class inherits from :class:`aspecd.metadata.Sample`,
    see the documentation of the parent class for details and the full list
    of inherited attributes.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    description : :class:`str`
        Description of the measured sample.

    solvent : :class:`str`
        Name of the solvent used.

    preparation : :class:`str`
        Short details of the sample preparation.

    tube : :class:`str`
        Type and dimension of the sample tube used.

    """

    def __init__(self, dict_=None):
        # public properties
        self.description = ''
        self.solvent = ''
        self.preparation = ''
        self.tube = ''
        super().__init__(dict_=dict_)


class MagneticField(aspecd.metadata.Metadata):
    """Metadata corresponding to the magnetic field.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    start : :class:`aspecd.metadata.PhysicalQuantity`
        Lowest point of the magnetic field.

    stop : :class:`aspecd.metadata.PhysicalQuantity`
        Highest point of the magnetic field.

    sweep_width : :class:`aspecd.metadata.PhysicalQuantity`
        Width of the magnetic field sweep.

    step_width : :class:`aspecd.metadata.PhyPhysicalQuantity`
        Distance between two points (only if equidistant!).

    points : :class:`int`
        Number of points.

    field_probe_type : :class:`str`
        Type of the field probe (e.g. Hall or Teslameter)

    field_probe_model : :class:`str`
        Exact model of the field probe.

    sequence : :class:`str`
        Sequence of the experiment (e.g. up or down).

    controller : :class:`str`
        Model of the field controller.

    power_supply : :class:`str`
        Model of the power supply.

    """

    def __init__(self, dict_=None):
        super().__init__(dict_=dict_)
        self.start = aspecd.metadata.PhysicalQuantity()
        self.stop = aspecd.metadata.PhysicalQuantity()
        self.sweep_width = aspecd.metadata.PhysicalQuantity()
        self.step_width = aspecd.metadata.PhysicalQuantity()
        self.points = int()
        self.field_probe_type = ""
        self.field_probe_model = ""
        self.sequence = ""
        self.controller = ""
        self.power_supply = ""

    def can_calculate(self):
        """Check if enough data is present to determine field values.

        Checks if enough different pieces of information are provided to
        calculate all information concerning the field sector and sweeping
        steps.

        .. note::
            Currently, the possibility of calculating the sector width from the
            width and the number of steps is not accounted for.

        Raises
        ------
        NotEnoughValuesError
            Raised when not enough different pieces of information are provided
            to determine the other variables.

        """
        sector_def = False
        sector_par = 0
        step_def = False
        step_par = 0
        if self.start.value != 0.:
            sector_def = True
            sector_par += 1
        if self.stop.value != 0.:
            sector_def = True
            sector_par += 1
        if self.sweep_width.value != 0.:
            sector_par += 1
            step_par += 1
        if self.points != 0:
            step_def = True
            step_par += 1
        if (not sector_def) or sector_par < 2:
            raise ValueError("Sector not determined.")
        if (not step_def) or step_par < 2:
            raise ValueError("Steps not determined.")
        return True

    def calculate_values(self):
        """Perform the calculation of all field values left out.

        Calculate the different values concerning the sector and sweeping steps
        of the magnetic field.

        .. note::
            Currently, the possibility of calculating the sector width from the
            with and the number of steps is not accounted for.

        Raises
        ------
        UnequalUnitsError :
            Raised, when two physical quantities shall be added or subtracted
            that have unequal units.

        """
        units_error_message = "Quantities with different units provided."
        if self.can_calculate():
            self.points = int(self.points)
            self._calc_field_width(units_error_message)
            self._calc_field_limits(units_error_message)
            self._calc_step_data(units_error_message)

    def _calc_field_width(self, units_error_message):
        if self.sweep_width.value == 0.:
            if self.stop.unit != self.start.unit:
                raise UnequalUnitsError(units_error_message)
            self.sweep_width.value = self.stop.value - self.start.value
            self.sweep_width.unit = self.stop.unit

    def _calc_field_limits(self, units_error_message):
        if self.stop.value == 0.:
            if self.sweep_width.unit != self.start.unit:
                raise UnequalUnitsError(units_error_message)
            self.stop.value = self.start.value + self.sweep_width.value
            self.stop.unit = self.start.unit
        if self.start.value == 0.:
            if self.stop.unit != self.sweep_width.unit:
                raise UnequalUnitsError(units_error_message)
            self.start.value = self.stop.value - self.sweep_width.value
            self.start.unit = self.stop.unit

    def _calc_step_data(self, units_error_message):
        if self.points == 0:
            if self.sweep_width.unit != self.step_width.unit:
                raise UnequalUnitsError(units_error_message)
            self.points = int(round((self.sweep_width.value /
                                     self.step_width.value), 0)) + 1
        if self.step_width.value == 0.:
            self.step_width.value = \
                self.sweep_width.value / (self.points - 1)
            self.step_width.unit = self.stop.unit

    def gauss_to_millitesla(self):
        """Transform magnetic field parameters from gauss to millitesla."""
        for quantity in [self.start, self.stop,
                         self.sweep_width, self.step_width]:
            quantity.value /= 10
            quantity.unit = "mT"


class Experiment(aspecd.metadata.Metadata):
    """Metadata corresponding to the experiment.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing properties to set.

    Attributes
    ----------
    type : :class:`str`

    runs : :class:`int`
        Number of recorded runs.

    variable_parameter : :class:`str`
        Parameter that is varied during the measurement, e.g. *magnetic field*

    increment : :class:`str`
        Increment the variable parameter is changed.

    harmonic : :class:`str`
        Recorded harmonic of the signal.

    """

    def __init__(self, dict_=None):
        self.type = ""
        self.runs = None
        self.variable_parameter = ""
        self.increment = None
        self.harmonic = None
        super().__init__(dict_=dict_)


class Spectrometer(aspecd.metadata.Metadata):
    """Metadata information on what type of spectrometer was used.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing properties to set.

    Attributes
    ----------
    model : :class:`str`
        Model of the spectrometer used.

    software : :class:`str`
        Name and version of the software used.

    """

    def __init__(self, dict_=None):
        self.model = ""
        self.software = ""
        super().__init__(dict_=dict_)


class Bridge(aspecd.metadata.Metadata):
    """Metadata corresponding to the microwave bridge.

    The microwave bridge contains the microwave source and parts of the
    detection system. Therefore, the crucial experimental parameters such as
    attenuation and power, microwave frequency and detection system used are
    contained as well as the description of the devices, *i.e.* the bridge
    itself, its controller, and the frequency counter, as these can be
    different interchangeable components.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    model : :class:`str`
        Model of the microwave bridge used.

    controller : :class:`str`
        Model of the bridge controller used.

    attenuation : :class:`aspecd.metadata.PhysicalQuantity`
        Attenuation of the microwave power in dB.

        Without knowing the unattenuated source power, the attenuation is a
        rather useless value, although it gets often used, particularly in
        lab jargon. Typical microwave bridges have source powers of 200 mW
        in X-Band, but newer devices sometimes deliver only 150 mW.

    power : :class:`aspecd.metadata.PhysicalQuantity`
        Output power of the microwave.

        The actual output power of the microwave used for the experiment,
        *i.e.* the source power reduced by the attenuation. Typical values
        are in the range of 20 mW to 20 µW.

    detection : :class:`str`
        Type of the detection used.

        There are two types of detection: diode and mixer. The latter
        usually allows for quadrature detection, *i.e.* detecting both, the
        absorptive and dispersive signal components.

    frequency_counter : :class:`str`
        Model of the frequency counter used.

        Depending on the setup used, this can be included in the bridge.
        Otherwise, it will often be a HP device.

    mw_frequency : :class:`aspecd.metadata.PhysicalQuantity`
        Microwave frequency.

        The actual microwave frequency used for the experiment. Usually,
        this is a scalar number. Depending on the experiment control
        software used, the microwave frequency for each transient will be
        recorded, thus allowing for analysing frequency drifts. This is
        particularly helpful in case of long-running experiments (12+ h).
        By comparing the amplitude of the frequency drift with the field
        step width, the potential impact in the signal shape can be directly
        calculated.

    q_value : :class:`int`
        Quality factor of the cavity.

        In most spectrometers, acquiring the Q-factor is not done by hand
        i.e. in Bruker spectrometers the measurement ist most commonly
        performed in tune mode with an attenuation of 33 dB, whereas at the
        Magnettech benchtop spectrometer, one has to select the box to
        measure the Q-factor.

    """

    def __init__(self, dict_=None):
        self.model = ""
        self.controller = ""
        self.attenuation = aspecd.metadata.PhysicalQuantity()
        self.power = aspecd.metadata.PhysicalQuantity()
        self.detection = ""
        self.frequency_counter = ""
        self.mw_frequency = aspecd.metadata.PhysicalQuantity()
        self.q_value = 0
        super().__init__(dict_=dict_)


class SignalChannel(aspecd.metadata.Metadata):
    """Metadata information information on the signal channel employed.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    model : :class:`str`
        Model of the signal channel.

    modulation_amplifier : :class:`str`
        Type of the modulation amplifier.

    accumulations : :class:`int`
        Number of accumulated scans.

    modulation_frequency : :class:`aspecd.metadata.PhysicalQuantity`
        Modulation frequency used.

    modulation_amplitude : :class:`aspecd.metadata.PhysicalQuantity`
        Amplitude of the modulation

    receiver_gain : :class:`aspecd.metadata.PhysicalQuantity`
        Gain of the receiver, existence depends on the spectrometer.

    conversion_time : :class:`aspecd.metadata.PhysicalQuantity`
        Conversion time (usually in ms).

    time_constant : :class:`aspecd.metadata.PhysicalQuantity`
        Time constant (usually in ms).

    phase : :class:`aspecd.metadata.PhysicalQuantity`
        Phase of the modulation amplifier.

    offset : :class:`float`
        Baseline offset

    """

    def __init__(self, dict_=None):
        self.model = ""
        self.modulation_amplifier = ""
        self.accumulations = int()
        self.modulation_frequency = aspecd.metadata.PhysicalQuantity()
        self.modulation_amplitude = aspecd.metadata.PhysicalQuantity()
        self.receiver_gain = aspecd.metadata.PhysicalQuantity()
        self.conversion_time = aspecd.metadata.PhysicalQuantity()
        self.time_constant = aspecd.metadata.PhysicalQuantity()
        self.phase = aspecd.metadata.PhysicalQuantity()
        self.offset = float()
        super().__init__(dict_=dict_)


class Probehead(aspecd.metadata.Metadata):
    """Metadata corresponding to the probehead.

    Often, resonating structures get used in EPR spectroscopy, but as this
    is not always the case, the term "probehead" is more generic.

    In all except of fully integrated benchtop spectrometers, the probehead
    can readily be exchanged. As each probehead has its own characteristics,
    it is crucially important to note at least type and model. The coupling
    (critically or overcoupled) determines the bandwidth of the resonator,
    and in all but pulsed experiments, usually, critical coupling is used.


    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing properties to set.


    Attributes
    ----------
    type : :class:`str`
        Type of the probehead used.

        There are several different types of probeheads regularly used. For
        resonators, there are, *e.g.*, dielectic and split-ring resonators,
        cylindrical and rectangular cavities. More special would be
        Fabry-Perot and stripline resonators. Sometimes, even resonator-free
        designs are used as probeheads.

    model : :class:`str`
        Model of the probehead used.

        Commercial probeheads come with a distinct model that goes in here.
        In all other cases, use a short, memorisable, and unique name.

    coupling : :class:`str`
        Type of coupling. In cwepr it is usually critically coupled.

    """

    def __init__(self, dict_=None):
        self.type = ""
        self.model = ""
        self.coupling = ""
        super().__init__(dict_=dict_)


class TemperatureControl(aspecd.metadata.TemperatureControl):
    """Metadata corresponding to the temperature control.

    As this class inherits from :class:`aspecd.metadata.TemperatureControl`,
    see the documentation of the parent class for details and the full list
    of inherited attributes.


    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing properties to set.

    Attributes
    ----------
    cryostat : :class:`str`
        Model of the cryostat used.

    cryogen : :class:`str`
        Cryogen used.

        Typically, this is either N2 (for temperatures down to 80K) or He
        (for temperatures down to 4 K)

    """

    def __init__(self, dict_=None):
        # public properties
        self.cryostat = ''
        self.cryogen = ''
        super().__init__(dict_=dict_)
