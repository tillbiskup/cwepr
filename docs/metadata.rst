================================
Metadata during data acquisition
================================

(Numerical) data without accompanying metadata are pretty useless, as data can only be analysed (and the results somewhat reproduced) knowing the context of their recording, *i.e.* what (instrumental) parameters have been used for data acquisition and what sample has been measured. While the cwepr package takes care of recording all metadata acquired *during* data processing and analysis, thanks to being based on the `ASpecD framework <https://docs.aspecd.de/>`, we are here concerned with **metadata during data acquisition**, *i.e.* the step before the cwepr package enters the stage.

.. important::

    While most spectrometers automatically record *some* instrumental parameters and include them in the vendor file format, usually these parameters are *not sufficiently complete*, and essential information such as what sample has been measured (by whom) is regularly not included. Hence, **you need to manually record essential metadata during data acquisition**, and to allow the cwepr package to access these crucial metadata, you better use a file format that can automatically be imported together with the data.


The Infofile format
===================

Recording metadata during data acquisition is both, an essential aspect of and as old as science itself. The Infofile format is a simple textual file format developed to **document research data**. It allows researchers in the lab to record all relevant metadata **during data acquisition** in a user-friendly and obvious way while minimising any external dependencies. The resulting machine-actionable metadata in turn allow processing and analysis software to access relevant information, besides **making the research data more reproducible** and FAIRer.


.. tip::

    The cwepr package will automatically look for a file with the same base name and the extension ``.info`` when importing files. Hence, the clear advice is to make it a habit to record all relevant metadata in an Infofile *during data acquisition* and store it next to the actual data files.


Further information on the format including the full specification and a discussion of the advantages (and disadvantages) compared to other formats can be found in the following publication:

  * Bernd Paulus, Till Biskup: Towards more reproducible and FAIRer     research data: documenting provenance during data acquisition using the     Infofile format. *Digital Discovery* **2**:234–244, 2023, doi:`10.1039/D2DD00131D <https://doi.org/10.1039/D2DD00131D>`_

For actual Infofile example files, see the git repository available at GitHub:

  * https://github.com/tillbiskup/infofile

An example of a cw-EPR Infofile is provided below for convenience as well.


Features
--------

* Simple text format
* Storing structured, machine-actionable metadata
* Minimum formatting overhead
* Focussing on human-writability
* No external (software) dependencies
* Easily extendable


Benefits
--------

* No thinking required: never miss any relevant parameter
* All information for the materials&methods part always available (even for collaboration partners)
* Automatic import using the cwepr package: information available during data processing and analysis (and in reports)
* Big step forward towards *truly* reproducible research


Example
-------

Below is a full example of a Infofile for a cw-EPR measurement. The format should be pretty self-explaining. Whether you need every block depends on your setup and type of experiment. For templates and information regarding further development, see the corresponding `GitHub repository <https://github.com/tillbiskup/infofile>`_. A full format description is given in the `accompanying publication <https://doi.org/10.1039/D2DD00131D>`_.


.. literalinclude:: cwepr.info


Metadata and commercial EPR spectrometers
=========================================

While many commercially available EPR spectrometers do include a number of parameters in their vendor file formats (*e.g.*, Bruker and Magnettech), these automatically obtained parameter values can have two problems:

* **Incomplete**

  More often than not, not all devices are directly connected to and controlled by the measurement program. Typical examples include temperature controllers. Those parameters cannot be obtained automatically by the measurement program and hence do not enter the parameter list of the written data files.

  Other parameters are not readable *per se*, such as the actual resonator/probehead in the spectrometer, and for older setups the individual components and their model numbers, including microwave bridge, signal channel, field controller, power supply and alike. However, all that information is crucial for a sensible materials&methods part of your publication.

* **Wrong**

  Even more problematic, some vendors do *not* save the data after the measurement finished, but only when the operator explicitly tells the measurement program to store the data to disk. What might sound only annoying (as you can easily loose your data) is yet a bigger problem: The parameter values read from the devices and stored in the parameters section of the vendor file format get read at the time point when the operator saves the file. Imagine a long-running measurement ending in the middle of the night, with several hours passing between end of measurement and pressing the "save" button in the software. Whatever instrumental parameter has changed in the meantime (prime example: drifting microwave frequency) gets saved with a potential wrong parameter. Even worse: if you happen to accidentally change some parameter settings after finishing the measurement and before storing the data, the new settings will be saved, not those used for performing the measurement.


While highly integrated benchtop spectrometers are somewhat better in this respect (no exchangeable components, higher integration), there is a need to both, record additional metadata not stored in the vendor file formats, and to record parameters that are contained in the vendor file formats but may be the wrong values.

