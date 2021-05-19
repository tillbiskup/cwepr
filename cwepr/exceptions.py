"""
Error classes for the io subpackage.

Currently, all error classes for the io subpackage are located in this
module. Whether this is a good idea remains to be seen. As the importers for
each vendor file format reside in their own module, but will share certain
error classes, it might, though.

"""


class Error(Exception):
    """Base class for exceptions in this module."""


class NoMatchingFilePairError(Error):
    """Exception raised when no pair of data and parameter file is found.

    Data and parameter files' extensions must match a single format.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class MissingPathError(Error):
    """Exception raised when no path is provided.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class MissingInfoFileError(Error):
    """Exception raised when no user created info file is found.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class ExperimentTypeError(Error):
    """Exception raised in case of problems with designated experiment type.

    This includes two cases:
    1) the data provided do not correspond to a cw experiment
    2) the experiment type cannot be determined.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class DimensionError(Error):
    """Exception indicating error in the dimension of an object.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingInformationError(Error):
    """Exception raised when not enough information is provided."""

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class SpectrumNotIntegratedError(Error):
    """Exception raised when definite integration is used accidentally.

    Definite integration should only be performed on a derivative spectrum.

    Attributes
    ----------
    message : :class:`str`
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


class RecipeNotFoundError(Error):
    """Exception raised when a recipe could not be found.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message