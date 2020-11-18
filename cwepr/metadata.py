"""Metadata

Supplementary data for a dataset, i.e. everything that is not part of the
literal experimental results, such as identifier, date of the experiment...
"""


import aspecd.metadata


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class NotEnoughValuesError(Error):
    """Exception raised when not enough data is given for a mathematical task.

    This happens when not enough different values are provided to calculate all
    other values.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UnequalUnitsError(Error):
    """Exception raised when addends have unequal units.

    This is relevant when two physical quantities that shall be added or
    subtracted do not have the same unit.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class DatasetMetadata(aspecd.metadata.ExperimentalDatasetMetadata):
    """Set of all metadata for a dataset object.

    Attributes
    ----------
    experiment: :obj:`cwepr.metadata.Experiment`
        Metadata object containing information such as the type of the
        experiment performed.

    spectrometer: :obj:`cwepr.metadata.Spectrometer`
        Metadata object containing information on the spectrometer used.

    magnetic_field: :obj:`cwepr.metadata.MagneticField`
        Metadata object containing information on the magnetic field applied in
        the experiment.

    bridge: :obj:`cwepr.metadata.Bridge`
        Metadata object containing information on the microwave bridge used.

    signal_channel: :obj:`cwepr.metadata.SignalChannel`
        Metadata object containing information on the signal channel applied.

    probehead: :obj:`cwepr.metadata.Probehead`
        Metadata object containing information on the probehead used in the
        experiment.

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


class Measurement(aspecd.metadata.Measurement):
    """Metadata corresponding to the measurement.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    label : str
        Label of the sample, including the sample-number.

    """

    def __init__(self, dict_=None):
        # public properties
        self.label = ''
        super().__init__(dict_=dict_)


class Sample(aspecd.metadata.Sample):
    """Metadata information on the sample measured."""

    def __init__(self):
        super().__init__()
        self.solvent = ""


class MagneticField(aspecd.metadata.Metadata):
    """Metadata class including all variables concerning the magnetic field."""

    def __init__(self, dict_=None):
        super().__init__(dict_=dict_)
        self.start = aspecd.metadata.PhysicalQuantity()
        self.stop = aspecd.metadata.PhysicalQuantity()
        self.sweep_width = aspecd.metadata.PhysicalQuantity()
        self.step_width = aspecd.metadata.PhysicalQuantity()
        # Should not be used in the future
        self.step_count = 0
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
        if self.step_width.value != 0.:
            step_def = True
            step_par += 1
        if self.step_count != 0:
            step_def = True
            step_par += 1
        if (not sector_def) or sector_par < 2:
            raise NotEnoughValuesError("Sector not determined.")
        if (not step_def) or step_par < 2:
            raise NotEnoughValuesError("Steps not determined.")
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
            self.step_count = int(self.step_count)
            self._calc_field_width(units_error_message)
            self._calc_field_limits(units_error_message)
            self._calc_step_data(units_error_message)

    def _calc_field_width(self, units_error_message):
        if self.sweep_width.value == 0.:
            if self.stop.unit != self.start.unit:
                raise UnequalUnitsError(units_error_message)
            self.sweep_width.value = self.stop.value - \
                                     self.start.value
            self.sweep_width.unit = self.stop.unit

    def _calc_field_limits(self, units_error_message):
        if self.stop.value == 0.:
            if self.sweep_width.unit != self.start.unit:
                raise UnequalUnitsError(units_error_message)
            self.stop.value = self.start.value + \
                              self.sweep_width.value
            self.stop.unit = self.start.unit
        if self.start.value == 0.:
            if self.stop.unit != self.sweep_width.unit:
                raise UnequalUnitsError(units_error_message)
            self.start.value = self.stop.value - \
                               self.sweep_width.value
            self.start.unit = self.stop.unit

    def _calc_step_data(self, units_error_message):
        if self.step_count == 0:
            if self.sweep_width.unit != self.step_width.unit:
                raise UnequalUnitsError(units_error_message)
            self.step_count = int(round((self.sweep_width.value /
                                         self.step_width.value), 0)) + 1
        if self.step_width.value == 0.:
            self.step_width.value = self.sweep_width.value / \
                                    (self.step_count - 1)
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

    """

    def __init__(self, dict_=None):
        self.type = ""
        self.runs = None
        self.variable_parameter = ""
        self.increment = None
        self.harmonic = None
        super().__init__(dict_=dict_)


class Spectrometer(aspecd.metadata.Metadata):
    """Metadata information on what type of spectrometer was used."""

    def __init__(self, dict_=None):
        self.model = ""
        self.software = ""
        super().__init__(dict_=dict_)


class Bridge(aspecd.metadata.Metadata):
    """Metadata corresponding to the bridge.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    model : str
        Model of the microwave bridge used.

    controller : str
        Model of the bridge controller used.

    attenuation : :obj:`aspecd.metadata.PhysicalQuantity`
        Attenuation of the microwave in dB.

    power : :obj:`aspecd.metadata.PhysicalQuantity`
        Output power of the microwave.

    detection : str
        Type of the detection used.

    frequency_counter : str
        Model of the frequency counter used.

    mw_frequency : :obj:`aspecd.metadata.PhysicalQuantity`
        Microwave frequency.

    q_value : int
        Quality factor of the cavity

    """

    def __init__(self, dict_=None):
        self.model = ""
        self.controller = ""
        self.attenuation = aspecd.metadata.PhysicalQuantity()
        self.power = aspecd.metadata.PhysicalQuantity()
        self.detection = ""
        self.frequency_counter = ""
        self.mw_frequency = aspecd.metadata.PhysicalQuantity()
        self.q_value = None
        super().__init__(dict_=dict_)


class SignalChannel(aspecd.metadata.Metadata):
    """Metadata information information on the signal channel employed."""

    def __init__(self, dict_=None):
        self.model = ""
        self.modulation_amplifier = ""
        self.accumulations = ""
        self.modulation_frequency = aspecd.metadata.PhysicalQuantity()
        self.modulation_amplitude = aspecd.metadata.PhysicalQuantity()
        self.receiver_gain = aspecd.metadata.PhysicalQuantity()
        self.conversion_time = aspecd.metadata.PhysicalQuantity()
        self.time_constant = aspecd.metadata.PhysicalQuantity()
        self.phase = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Probehead(aspecd.metadata.Metadata):
    """Metadata corresponding to the probehead.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    type : str
        Type of the probehead used.

    model : str
        Model of the probehead used.

    coupling : str
        Type of coupling.

    """

    def __init__(self, dict_=None):
        self.type = ""
        self.model = ""
        self.coupling = ""
        super().__init__(dict_=dict_)


class TemperatureControl(aspecd.metadata.TemperatureControl):
    """Metadata corresponding to the temperature control.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    cryostat : str
        Model of the cryostat used.

    cryogen : str
        Cryogen used.

    """

    def __init__(self, dict_=None):
        # public properties
        self.cryostat = ''
        self.cryogen = ''
        super().__init__(dict_=dict_)
