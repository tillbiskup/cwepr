"""Metadata

Supplementary data for a dataset, i.e. everything that is not
part of the literal experimental results, such as identifier,
date of the experiment..."""


import aspecd.metadata


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class NotEnoughValuesError(Error):
    """Exception raised when not enough different values
    are provided to calculate all other values.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UnequalUnitsError(Error):
    """

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class DatasetMetadata(aspecd.metadata.DatasetMetadata):
    """Set of all metadata for a dataset object.

     Attributes
    ----------
    modifications : 'list'
        List of all modifications performed on the metadata.

    """
    def __init__(self):
        super().__init__()
        self.experiment = Experiment()
        self.spectrometer = SpectrometerInfo()
        self.magnetic_field = BFieldData()
        self.bridge = BridgeInfo()
        self.signal_channel = SignalChannel()
        self.probehead = Probehead()
        self.modifications = []


class BFieldData(aspecd.metadata.Metadata):
    """"""

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
        if self.can_calculate():
            self.step_count = int(self.step_count)
            if self.field_width.value == 0.:
                if self.field_max.unit != self.field_min.unit:
                    raise UnequalUnitsError("Quantities with different units provided.")
                self.field_width.value = self.field_max.value - self.field_min.value
                self.field_width.unit = self.field_max.unit
            if self.field_max.value == 0.:
                if self.field_width.unit != self.field_min.unit:
                    raise UnequalUnitsError("Quantities with different units provided.")
                self.field_max.value = self.field_min.value + self.field_width.value
                self.field_max.unit = self.field_min.unit
            if self.field_min.value == 0.:
                if self.field_max.unit != self.field_width.unit:
                    raise UnequalUnitsError("Quantities with different units provided.")
                self.field_min.value = self.field_max.value - self.field_width.value
                self.field_min.unit = self.field_max.unit
            if self.step_count == 0:
                if self.field_width.unit != self.step_width.unit:
                    raise UnequalUnitsError("Quantities with different units provided.")
                self.step_count = self.field_width.value - self.step_width.value + 1
            if self.step_width.value == 0.:
                self.step_width.value = self.field_width.value / (self.step_count - 1)
                self.step_width.unit = self.field_max.unit

    def gauss_to_millitesla(self):
        for quantity in [self.field_min, self.field_max, self.field_width, self.step_width]:
            quantity.value /= 10
            quantity.unit = "mT"


class Experiment(aspecd.metadata.Metadata):
    """"""

    def __init__(self):
        super().__init__()
        self.type = ""
        self.runs = ""
        self.variable_parameter = ""
        self.increment = ""
        self.harmonic = ""


class SpectrometerInfo(aspecd.metadata.Metadata):
    """"""

    def __init__(self):
        super().__init__()
        self.model = ""
        self.software = ""


class BridgeInfo(aspecd.metadata.Metadata):
    """"""

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
    """"""

    def __init__(self):
        super().__init__()
        self.model = ""
        self.modulation_amplifier = ""
        self.accumulations = ""
        self.modulation_frequency = aspecd.metadata.PhysicalQuantity()
        self.modulation_amplitude = aspecd.metadata.PhysicalQuantity()
        self.receiver_gain = aspecd.metadata.PhysicalQuantity()
        self.conversion_time = aspecd.metadata.PhysicalQuantity()
        self.time_constant = ""
        self.phase = aspecd.metadata.PhysicalQuantity()


class Probehead(aspecd.metadata.Metadata):
    """"""

    def __init__(self):
        super().__init__()
        self.type = ""
        self.model = ""
        self.coupling = ""
