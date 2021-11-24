"""Datasets: units containing data and metadata.

The dataset is one key concept of the ASpecD framework and hence the cwepr
package derived from it, consisting of the data as well as the corresponding
metadata. Storing metadata in a structured way is a prerequisite for a
semantic understanding within the routines. Furthermore, a history of every
processing, analysis and annotation step is recorded as well, aiming at a
maximum of reproducibility. This is part of how the ASpecD framework and
therefore the cwepr package tries to support good scientific practice.

Therefore, each processing and analysis step of data should always be
performed using the respective methods of a dataset, at least as long as it
can be performed on a single dataset.

Datasets
========

Generally, there are two types of datasets: Those containing experimental
data and those containing calculated data. Therefore, two corresponding
subclasses exist:

  * :class:`cwepr.dataset.ExperimentalDataset`
  * :class:`cwepr.dataset.CalculatedDataset`


Dataset factory
===============

Particularly in case of recipe-driven data analysis (c.f. :mod:`aspecd.tasks`),
there is a need to automatically retrieve datasets using nothing more than a
source string that can be, e.g., a path or LOI. This is where the
DatasetFactory comes in. This is a factory in the sense of the factory
pattern described by the "Gang of Four" in their seminal work, "Design
Patterns" (Gamma et al., 1995):

  * :class:`cwepr.dataset.DatasetFactory`


Module documentation
====================
"""

import aspecd.dataset
import aspecd.utils

import cwepr.io.factory
import cwepr.metadata


class ExperimentalDataset(aspecd.dataset.ExperimentalDataset):
    """Set of data uniting all relevant information.

    The unity of numerical and metadata is indispensable for the
    reproducibility of data and is possible by saving all information available
    for one set of measurement data in a single instance of this class.
    """

    def __init__(self):
        super().__init__()
        self.metadata = cwepr.metadata.ExperimentalDatasetMetadata()


class CalculatedDataset(aspecd.dataset.CalculatedDataset):
    """Entity consisting of calculated data and metadata.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.dataset.CalculatedDataset`
    class for details.

    """


class DatasetFactory(aspecd.dataset.DatasetFactory):
    """
    Factory for creating dataset objects based on the source provided.

    Particularly in case of recipe-driven data analysis (c.f.
    :mod:`aspecd.tasks`),
    there is a need to automatically retrieve datasets using nothing more
    than a source string that can be, e.g., a path or LOI.

    The DatasetFactory operates in conjunction with a
    :class:`cwepr.io.factory.DatasetImporterFactory` to import the actual
    dataset. See the respective class documentation for more details.


    Attributes
    ----------
    importer_factory : :class:`cwepr.io.factory.DatasetImporterFactory`
        ImporterFactory instance used for importing datasets

    """

    def __init__(self):
        super().__init__()
        self.importer_factory = cwepr.io.factory.DatasetImporterFactory()

    @staticmethod
    def _create_dataset(source=''):
        """Return cwepr dataset.

        Parameters
        ----------
        source : :class:`str`
            string describing the source of the dataset

            May be a filename or path, a URL/URI, a LOI, or similar

        Returns
        -------
        dataset : :class:`cwepr.dataset.ExperimentalDataset`
            Dataset object for cwepr package

        """
        return cwepr.dataset.ExperimentalDataset()
