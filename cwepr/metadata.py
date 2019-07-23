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
        self.experiment = Experiment()
        self.sample = Sample()
        self.spectrometer = Spectrometer()
        self.magnetic_field = MagneticField()
        self.bridge = Bridge()
        self.signal_channel = SignalChannel()
        self.probehead = Probehead()
        self.metadata_modifications = []


class Sample(aspecd.metadata.Sample):
    """Metadata information on the sample measured."""

    def __init__(self):
        super().__init__()
        self.solvent = ""


class MagneticField(aspecd.metadata.Metadata):
    """Metadata class including all variables concerning the magnetic field."""

    def __init__(self, dict_=None):
        super().__init__(dict_=dict_)
        self.field_min = aspecd.metadata.PhysicalQuantity()
        self.field_max = aspecd.metadata.PhysicalQuantity()
        self.field_width = aspecd.metadata.PhysicalQuantity()
        self.step_width = aspecd.metadata.PhysicalQuantity()
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
        if self.field_min.value != 0.:
            sector_def = True
            sector_par += 1
        if self.field_max.value != 0.:
            sector_def = True
            sector_par += 1
        if self.field_width.value != 0.:
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
        if self.field_width.value == 0.:
            if self.field_max.unit != self.field_min.unit:
                raise UnequalUnitsError(units_error_message)
            self.field_width.value = self.field_max.value - \
                self.field_min.value
            self.field_width.unit = self.field_max.unit

    def _calc_field_limits(self, units_error_message):
        if self.field_max.value == 0.:
            if self.field_width.unit != self.field_min.unit:
                raise UnequalUnitsError(units_error_message)
            self.field_max.value = self.field_min.value + \
                self.field_width.value
            self.field_max.unit = self.field_min.unit
        if self.field_min.value == 0.:
            if self.field_max.unit != self.field_width.unit:
                raise UnequalUnitsError(units_error_message)
            self.field_min.value = self.field_max.value - \
                self.field_width.value
            self.field_min.unit = self.field_max.unit

    def _calc_step_data(self, units_error_message):
        if self.step_count == 0:
            if self.field_width.unit != self.step_width.unit:
                raise UnequalUnitsError(units_error_message)
            self.step_count = int(round((self.field_width.value /
                                         self.step_width.value), 0)) + 1
        if self.step_width.value == 0.:
            self.step_width.value = self.field_width.value / \
                (self.step_count - 1)
            self.step_width.unit = self.field_max.unit

    def gauss_to_millitesla(self):
        """Transform magnetic field parameters from gauss to millitesla."""
        for quantity in [self.field_min, self.field_max,
                         self.field_width, self.step_width]:
            quantity.value /= 10
            quantity.unit = "mT"


class Experiment(aspecd.metadata.Metadata):
    """General information on what type of experiment was performed."""

    def __init__(self):
        super().__init__()
        self.type = ""
        self.runs = ""
        self.variable_parameter = ""
        self.increment = ""
        self.harmonic = ""


class Spectrometer(aspecd.metadata.Metadata):
    """Metadata information on what type of spectrometer was used."""

    def __init__(self):
        super().__init__()
        self.model = ""
        self.software = ""


class Bridge(aspecd.metadata.Metadata):
    """Metadata information on the microwave bridge employed."""

    def __init__(self):
        super().__init__()
        self.model = ""
        self.controller = ""
        self.attenuation = aspecd.metadata.PhysicalQuantity()
        self.power = aspecd.metadata.PhysicalQuantity()
        self.detection = ""
        self.frequency_counter = ""
        self.mw_frequency = aspecd.metadata.PhysicalQuantity()
        self.q_value = ""


class SignalChannel(aspecd.metadata.Metadata):
    """Metadata information information on the signal channel employed."""

    def __init__(self):
        super().__init__()
        self.model = ""
        self.modulation_amplifier = ""
        self.accumulations = ""
        self.modulation_frequency = aspecd.metadata.PhysicalQuantity()
        self.modulation_amplitude = aspecd.metadata.PhysicalQuantity()
        self.receiver_gain = aspecd.metadata.PhysicalQuantity()
        self.conversion_time = aspecd.metadata.PhysicalQuantity()
        self.time_constant = aspecd.metadata.PhysicalQuantity()
        self.phase = aspecd.metadata.PhysicalQuantity()


class Probehead(aspecd.metadata.Metadata):
    """Metadata information on the probe head employed."""

    def __init__(self):
        super().__init__()
        self.type = ""
        self.model = ""
        self.coupling = ""
