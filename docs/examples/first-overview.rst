===============================
First overview of a measurement
===============================

Measuring cw-EPR spectra of samples often results in a series of measurements, and one of the first tasks is to get an overview what has been measured and how the results look like.

To this end, a series of tasks needs to be performed on each dataset:

#. Baseline correction (at least zeroth-order)

#. Frequency correction (to be comparable)

#. Simple plot for graphical display of recorded data

Furthermore, it can be quite useful to automatically generate a well-formatted report including the metadata (such as the parameters and settings used to record the data) as well.


.. literalinclude:: first-overview.yaml
    :language: yaml
    :linenos:
    :caption: Complete recipe for getting a first overview of a recorded spectrum, with zeroth-oder baseline correction, frequency correction, a simple 1D plot, and a report covering as well the metadata contained in the dataset.

