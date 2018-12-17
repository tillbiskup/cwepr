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


class DatasetMetadata(aspecd.metadata.Metadata):
    """Set of all metadata for a dataset object.

     Attributes
    ----------
    modifications : 'list'
        List of all modifications performed on the metadata.

    """
    def __init__(self):
        super().__init__()
        self.modifications = []


class BFieldData(aspecd.metadata.Metadata):
    """"""

    def __init__(self, dict_=None):
        super().__init__(dict_=dict_)
        self.field_min = None
        self.field_max = None
        self.field_width = None
        self.step_width = None
        self.step_count = None

    def can_calculate(self):
        if not self.step_width and not self.step_count:
            raise NotEnoughValuesError("Steps not determined.")
        sector_params = 0
        for p in [self.field_max, self.field_min, self.field_width]:
            if p is not None:
                sector_params += 1
        if sector_params < 2:
            raise NotEnoughValuesError("Sector not determined.")
        return True

    def calculate_values(self):
        if self.can_calculate():
            pass




