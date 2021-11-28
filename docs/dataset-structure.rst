=================
Dataset structure
=================

The dataset is an essential :doc:`concept <concepts>` of the ASpecD framework and in turn the cwepr package, as it abstracts the different vendor formats and combines both, numerical data and metadata, in an easily accessible way. Even more, the general structure of a dataset allows to compare data of entirely different origin (read: spectroscopic method), as long as their axes are compatible.

Developers of the cwepr package frequently need to get an overview of the structure of the dataset and its different subclasses, namely the ``ExperimentalDataset`` and ``CalculatedDataset``. Whereas the API documentation of each class, :class:`cwepr.dataset.ExperimentalDataset` and :class:`cwepr.dataset.CalculatedDataset`, provides a lot of information, a simple and accessible presentation of the dataset structure is often what is needed.

Therefore, the structure of each of the dataset classes is provided below in YAML format, automatically generated from the actual source code.


Experimental dataset
====================

Entity containing both, numerical data as well as the corresponding metadata that are specific for the cw-EPR method. For implementation details, see the API documentation of :class:`cwepr.dataset.ExperimentalDataset` and :class:`cwepr.dataset.ExperimentalDatasetMetadata`.

.. literalinclude:: ExperimentalDataset.yaml
   :language: yaml


Calculated dataset
==================

Entity consisting of calculated data and corresponding metadata. For implementation details, see the API documentation of :class:`cwepr.dataset.CalculatedDataset`.

.. literalinclude:: CalculatedDataset.yaml
   :language: yaml

