"""General purpose functions and classes used in other modules.

To avoid circular dependencies, this module does *not* depend on any other
modules of the cwepr package, but it can be imported into every other module.

"""

import numpy as np
import scipy.constants


def convert_g2mT(values, mw_freq=None):
    """
    Convert *g* values to millitesla (mT)

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
    mu_b = scipy.constants.value('electron mag. mom.')

    return (planck_constant * mw_freq * 1e9) / (-mu_b * values * 1e-3)


def convert_mT2g(values, mw_freq=None):
    """
    Convert magnetic field values (in millitesla, mT) to *g* values

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
    mu_b = scipy.constants.value('electron mag. mom.')

    return (planck_constant * mw_freq * 1e9) / (-mu_b * values * 1e-3)
