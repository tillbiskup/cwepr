"""General purpose functions and classes used in other modules.

To avoid circular dependencies, this module does *not* depend on any other
modules of the cwepr package, but it can be imported into every other module.


.. versionadded:: 0.2

"""

import numpy as np
import scipy.constants


def convert_g2mT(values, mw_freq=None):  # noqa
    """
    Convert *g* values to millitesla (mT).

    .. important::

        Magnetic field values are assumed to be in **millitesla** (mT) and
        the microwave frequency to be in **Gigahertz** (GHz).


    Parameters
    ----------
    values : :class:`np.asarray` | :class:`float`
        *g* values to be converted into millitesla (mT)

    mw_freq : :class:`float`
        Microwave frequency (in GHz)

    Returns
    -------
    values : :class:`np.asarray` | :class:`float`
        converted values in millitesla (mT)

    """
    planck_constant = scipy.constants.value('Planck constant')
    mu_b = scipy.constants.value('Bohr magneton')

    values = np.asarray([not_zero(value) for value in values])
    return (planck_constant * mw_freq * 1e9) / (mu_b * values * 1e-3)


def convert_mT2g(values, mw_freq=None):  # noqa
    """
    Convert magnetic field values (in millitesla, mT) to *g* values.

    .. important::

        Magnetic field values are assumed to be in **millitesla** (mT) and
        the microwave frequency to be in **Gigahertz** (GHz).


    Parameters
    ----------
    values : :class:`np.asarray` | :class:`float`
        magnetic field values (in mT) to be converted to *g* values

    mw_freq :
        Microwave frequency (in GHz)

    Returns
    -------
    values : :class:`np.asarray` | :class:`float`
        converted values in *g*

    """
    planck_constant = scipy.constants.value('Planck constant')
    mu_b = scipy.constants.value('Bohr magneton')

    values = np.asarray([not_zero(value) for value in values])
    return (planck_constant * mw_freq * 1e9) / (mu_b * values * 1e-3)


def not_zero(value):
    """
    Return a value that is not zero to prevent DivisionByZero errors.

    Dividing by zero results in NaN values and often hinders evaluating
    mathematical models. A solution adopted from the lmfit Python package
    (https://doi.org/10.5281/zenodo.598352) returns a value equivalent to
    the resolution of a numpy float.

    .. note::

        If you use this function excessively within a module, mostly within
        rather complicated mathematical equations, it might be a good idea
        to import this function explicitly, to shorten the code, such as:
        ``from cwepr.utils import not_zero``. As usual, readability is king.

    Parameters
    ----------
    value : :class:`float`
        Value that can become (too close to) zero to trigger NaN values

    Returns
    -------
    value : :class:`float`
        Value guaranteed not to be zero

    """
    return np.copysign(max(abs(value), np.finfo(np.float64).resolution), value)
