r"""Importers for the NIEHS PEST file formats.

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1


The US National Institute of Environmental Health Sciences (NIEHS) provides
a collection of public epr software tools, abbreviated PEST. With those
software tools comes a collection of file formats used internally,
both binary and text-based.

For a general overview of PEST, see its homepage:

* https://www.niehs.nih.gov/research/resources/software/tox-pharm/tools/

All these file formats have in common that they contain rather few
metadata. Therefore, it is highly recommended that users provide metadata by
other means, at best in machine-readable format. One possibility would be
to use infofiles, as described in the respective :mod:`aspecd.infofile`
module.


Overview of file formats
========================

The PEST homepage provides an overview of the different file formats
available, for details see:

* https://www.niehs.nih.gov/research/resources/software/tox-pharm/tools/pest/

For convenience, the most important information is provided below:

==============  ============================================================
File extension  Description
==============  ============================================================
     .lmb       NIEHS exclusive binary format
     .exp       ASCII text format with various different realisations
     .dat       ASCII HP-PC interchange format
==============  ============================================================

Just to make things easier, the lmb format exists in two flavours,
with extensions ".lmb" and ".sim", the latter for simulated spectra.

Equally, the ASCII experimental spectra can exist in a plethora of
variations, according to the official documentation: with and without
header, with one or two columns, and with the first column being
magnetic field (in Gauss), time (in seconds), or g value. Interestingly
enough, though, the accepted input format is always two columns with
first column interpreted as magnetic field values.

Details of the individual file formats are given below. Eventually,
it is planned to support all three mentioned file formats.


.. _lmb_format:

NIEHS exclusive binary format (.lmb)
====================================

This file format is a binary format exclusively implemented to be used
with the NIEHS PEST suite. While it is somewhat documented, the best
documentation is still the C source code of the importer used to read the
format. Therefore, below a few more details will be given, together with
the C code used to implement the respective importer.

For authoritative details, the reader is referred to the following online
sources:

* https://www.niehs.nih.gov/research/resources/assets/docs/files.txt
* https://www.niehs.nih.gov/research/resources/assets/docs/files.c
* https://www.niehs.nih.gov/research/resources/assets/docs/constant.h
* https://www.niehs.nih.gov/research/resources/assets/docs/filename.h


General file architecture
-------------------------

The sequence of contents of a file in this format is as follows:

==========  =============  ===================================================
Type        Length         Description
==========  =============  ===================================================
identifier  4 byte         either ``ESRS`` or ``ESR2``
parameters  20x 4 byte     parameters, *e.g.*, for constructing field axis
data        *N*\ x 4 byte  actual data, number of points in parameters[2]
comment     60 byte        comment (in case of ``ESR2`` format, see below)
metadata    20x 12 byte    metadata, *e.g.*, microwave frequency
comments    2x 60 byte     additional comments in case of ``ESR2`` format
==========  =============  ===================================================


Parameter values
----------------

The parameters are not all used. The table below is extracted from the
documentation available at the NIEHS website. Note: Due to a slightly
strange way of using the loops in the original C source code (see below
for details), the number of the parameters in the table below is offset by
one. Furthermore, only those parameters with relevance for the import are
described.

=====  ====================================================================
#      Description
=====  ====================================================================
0      sweep width (in Gauss)
1      center field (in Gauss)
2      number of points
3-8    *unused here*
9      scan time in seconds
10-20  *unused here*
=====  ====================================================================


Metadata
--------
The metadata entries are not all used. The table below is extracted from the
documentation available at the NIEHS website. Note: Due to a slightly
strange way of using the loops in the original C source code (see below
for details), the number of the metadata entries in the table below is
offset by one. Furthermore, only those metadata with relevance for the
import are described.

=====  ====================================================================
#      Description
=====  ====================================================================
0-1    *unused here*
2      modulation amplitude
3      modulation frequency
4      time constant
5      receiver gain
6-7    *unused here*
8      microwave power
9      microwave frequency
10     date (unclear which one: start, end, saving of data)
11     time (unclear which one: start, end, saving of data)
12     scan time in seconds
13     sample temperature
14-20  *unused here*
=====  ====================================================================

.. note::
    Parameters 0-9 are typed in *manually*, therefore, never trust
    these values. Furthermore, due to their human origin, sometimes, value and
    unit are inconsistently separated (no separation, space, ...). Parameters
    10-20 are read from the spectrometer control software. Nevertheless,
    at least for the temperature, this does not mean that the field
    necessarily contains sensible values.


C code of NIEHS lmb importer (reference implementation)
--------------------------------------------------------

The C code shown below is abbreviated (only the important parts of the
files are shown), and it is only for reference. For details, see the
original sources available online from the NIEHS PEST website:

* https://www.niehs.nih.gov/research/resources/assets/docs/files.c
* https://www.niehs.nih.gov/research/resources/assets/docs/constant.h
* https://www.niehs.nih.gov/research/resources/assets/docs/filename.h

Furthermore, the copyright of the source code remains with its original
authors, namely Dave Duling (duling@niehs.nih.gov).


.. code-block:: c
    :caption: Abbreviated contents of the ``files.c`` file containing the
        PEST importer for lmb files. The source code of the two header files
        used is given below.

    /*
       files.c
       basic routines for reading and writing binary epr data files

       updated to use the new binary file format with expanded comments
    */

    #include <stdio.h>
    #include <string.h>
    #include <math.h>

    #include "constant.h"
    #include "filename.h"

    /**************************** READ FILE *****************************

     Read data for an import.  Deals with fpar, fstring, fnote0, and data

     return:   1 if error,   0 if no error.

    */
    int read_file( char *fname, double *ddata, float *fpar,
                   char fstring[][STRSIZE], char *fnote0,
                   char *fnote1, char *fnote2 )
    {

      FILE  *fp;
      int   i, ip;
      float fvalue;
      char  gstring[13];

      /* file not able to be read from */
      if ((fp = fopen(fname, "rb")) == NULL)  return(1);

      fread(gstring, 4, 1, fp);
      gstring[4] = '\0';

      if( strcmp(gstring, FILE_1)!=0 && strcmp(gstring, FILE_2 )!=0 ) {
         fclose(fp);
         return(1);			/* Not correct info. so exit */
      }

      for(i = 1; i <= MAX_PAR; ++i) 	/* read data parameters */
        fread(&fpar[i], 4, 1, fp);

      if( (int) fpar[3] > MAX_PTS ) {	/* check # data points	*/
        fclose(fp);
        return(1);
      }

      for(i = 1; i <= (int)fpar[3]; ++i) {	/* read data values     */
         fread(&fvalue, 4, 1, fp);
         ddata[i] = (double) fvalue;
      }

      fread(fnote0, 60, 1, fp);		/* read comment         */

      for(i = 1; i < STR_NUM ; ++i )	/* read strings         */
        fread( fstring[i], 12, 1, fp );

      if( strcmp(gstring, FILE_2)==0 ) {	/* read extra comments  */
        fread( fnote1, 60, 1, fp );
        fread( fnote2, 60, 1, fp );
      }

      fclose(fp);           /* close file           */
      return(0);            /* return success flag  */

    }  /* end of OPEN FILE */


.. code-block:: c
    :caption: Abbreviated contents of the ``constant.h`` file used in
        ``files.c`` shown above.

    /* constant.h

    */

    /* Define the number of datapoints based on the DOS restriction
       of 64KB of memory in one allocation unit.  Otherwise, use
       many more data points !
    */
    #ifdef DOS_LIMITED
      #define MAX_PTS     4096
      #define MAX_PTS2    2048
    #else
      #define MAX_PTS     16384
      #define MAX_PTS2    8192
    #endif

    /* this data not platform dependent */

    #define MAX_PAR     20
    #define STR_NUM     20
    #define STRSIZE     13
    #define COMMENTSIZE 61


.. code-block:: c
    :caption: Abbreviated contents of the ``filename.h`` file used in
        ``files.c`` shown above.

    /* filename.h

     Filename(s) & info constants
    */

    #define  FILE_1         "ESRS"
    #define  FILE_2         "ESR2"


To import files in this format, use the :class:`NIEHSLmbImporter`. Within
a recipe, the :class:`cwepr.io.factory.DatasetImporterFactory` should
automatically select the correct importer for you.


.. _exp_format:

NIEHS ASCII text format (.exp)
==============================

This text file format is actually a series of different formats, just to
make life easier. The most basic format simply contains (usually two)
columns with numerical data, but there are other versions as well with
additional information on top.

Two example files available from the NIEHS PEST website are documented below,
representing at least two different variants of this format (and currently
the only two variants supported by the respective importer class).


.. code-block::
    :caption: Plain text format containing only columns of data. This
        format is obviously trivial to read. The only tricky part for the
        importer is to distinguish it from the more detailed format shown
        below.

    3290.000	-1.5689E+01
    3290.945	1.5251E+01
    3291.890	2.8689E+00

.. code-block::
    :caption: Text format with additional parameters at the top.
        Presumably the first block contains some description of the data,
        *e.g.* related to a simulation. However, the NIEHS PEST website
        does not provide too much details.

    [EPR]
    N1: DMPO_OOH_OH spectrum S/N=5 with J.Bolton parameters
    N2: DMPO_OH:  aN= 15.3, aH= 15.3, 0.61, 0.25
    N3: DMPO_OOH: aN= 14.9, aH= 14.9

    [DATA]
    3295.10	-0.283
    3295.16	1.523
    3295.22	-0.964


To import files in this format, use the :class:`NIEHSExpImporter`. Within
a recipe, the :class:`cwepr.io.factory.DatasetImporterFactory` should
automatically select the correct importer for you.


.. _dat_format:

ASCII HP-PC interchange format (.dat)
=====================================

This text file format is a rather simple file format with four header
lines and only the intensities stored, but actually no metadata at all. An
example is given below:

.. code-block:: text

    ESRFILE
    50
    3359.27
    8192
    -12.234
       -5.48376
       -2.22887
       0.284066
       -0.698693


The first four lines have special meanings and are referred to as
"header", the following lines (up to the end of the file) are the actual
intensity values of the stored EPR spectrum.

=======  ==============================================================
Content  Description
=======  ==============================================================
ESRFILE  Identifier of the file type
50       scan range in Gauss (here: 50 G)
3359.27  center field in Gauss (here: 3359.27 G)
8192     number of data points (here: 8192) - usually a power of two
=======  ==============================================================

As mentioned above, all following lines contain just the intensity
values. Therefore, the importer needs to reconstruct the field axis
from the center field and scan range values provided. No further
metadata (such as microwave frequency) are available, therefore,
the spectra usually cannot be analysed appropriately unless the
missing information is provided by other means.

To import files in this format, use the :class:`NIEHSDatImporter`. Within
a recipe, the :class:`cwepr.io.factory.DatasetImporterFactory` should
automatically select the correct importer for you.


Module documentation
====================

"""
import io
import struct

import numpy as np

import aspecd.io
import aspecd.annotation


class NIEHSDatImporter(aspecd.io.DatasetImporter):
    """
    Importer for NIEHS PEST dat (text) files.

    The text file format dealt with here is a rather simple file format
    with four header lines and only the intensities stored, but actually
    no metadata at all.

    For details of the file format, see the section :ref:`dat_format`.

    .. note::
        Due to the lack of any metadata of this format, the resulting
        dataset is quite limited in its metadata. Only the axes measures
        and units are added (by informed guessing). Therefore, you are
        highly encouraged to provide the lacking metadata by other means.


    .. versionadded:: 0.3

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self._raw_data = None
        self._raw_metadata = {}

    def _import(self):
        self._clean_filenames()
        self._get_raw_data()
        self._import_data()
        self._create_axis()
        self._assign_units()
        self._assign_some_metadata()

    def _clean_filenames(self):
        # Dirty fix: Cut file extension
        if self.source.endswith((".dat", ".DAT")):
            self.source = self.source[:-4]

    def _get_raw_data(self):
        complete_filename = self.source + ".dat"
        self._raw_data = np.loadtxt(complete_filename, skiprows=1)

    def _import_data(self):
        self.dataset.data.data = self._raw_data[3:]

    def _create_axis(self):
        self._raw_metadata['center_field_mT'] = center_field = \
            self._raw_data[1] / 10
        self._raw_metadata['number_points'] = number_points = \
            int(self._raw_data[2])
        self._raw_metadata['sweep_width_mT'] = sweep_width = \
            self._raw_data[0] / 10
        self._raw_metadata['start'] = center_field - sweep_width / 2
        self._raw_metadata['stop'] = center_field + sweep_width / 2
        axis = np.linspace(center_field - sweep_width / 2,
                           center_field + sweep_width / 2,
                           num=number_points)
        assert axis[0] == center_field - sweep_width / 2
        self.dataset.data.axes[0].values = axis

    def _assign_units(self):
        self.dataset.data.axes[0].unit = 'mT'

    def _assign_some_metadata(self):
        self.dataset.metadata.magnetic_field.start.value = \
            self._raw_metadata['start']
        self.dataset.metadata.magnetic_field.stop.value = \
            self._raw_metadata['stop']
        self.dataset.metadata.magnetic_field.points = \
            self._raw_metadata['number_points']
        self.dataset.metadata.magnetic_field.sweep_width.value = \
            self._raw_metadata['sweep_width_mT']
        self.dataset.metadata.magnetic_field.sweep_width.unit = \
            self.dataset.metadata.magnetic_field.start.unit = \
            self.dataset.metadata.magnetic_field.stop.unit = 'mT'


class NIEHSLmbImporter(aspecd.io.DatasetImporter):
    """
    Importer for NIEHS PEST lmb (binary) files.

    This file format is a binary format exclusively implemented to be used
    with the NIEHS PEST suite.

    For details of the file format, see the section :ref:`lmb_format`.

    .. todo::
        Assign further metadata. Note that some metadata are entered
        manually, and therefore, parsing values with units with or without
        space between value and unit can be quite tricky.


    .. versionadded:: 0.3

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self._file_contents = None
        self._file_format = None
        self._parameters = {}
        self._metadata = {}
        self._position = 0
        self._comment = []

    def _import(self):
        self._clean_filenames()
        self._get_raw_data()
        self._detect_file_format()
        self._read_and_assign_parameters()
        self._read_data()
        self._read_comments_and_metadata()
        self._create_axis()
        self._assign_comment()
        self._assign_metadata()

    def _clean_filenames(self):
        # Dirty fix: Cut file extension
        if self.source.endswith((".lmb", ".sim")):
            self.source = self.source[:-4]

    def _get_raw_data(self):
        filename = self.source + ".lmb"
        with open(filename, 'rb') as file:
            self._file_contents = file.read()

    def _detect_file_format(self):
        self._file_format = self._file_contents[:4].decode('utf-8')

    def _read_and_assign_parameters(self):
        parameters = []
        self._position = 4
        max_par = 20
        for _ in range(max_par):
            parameters.append(
                struct.unpack(
                    'f',
                    self._file_contents[self._position:
                                        self._position + 4])[0])
            self._position += 4
        # Note: Only assign those parameters necessary in the given context
        self._parameters = {
            "sweep_width": parameters[0] / 10,
            "center_field": parameters[1] / 10,
            "n_points": int(parameters[2]),
            "scan_time": parameters[9],
        }

    def _read_data(self):
        data = []
        for _ in range(int(self._parameters["n_points"])):
            data.append(
                struct.unpack(
                    'f',
                    self._file_contents[self._position:
                                        self._position + 4])[0])
            self._position += 4
        self.dataset.data.data = np.asarray(data)

    # noinspection GrazieInspection
    def _read_comments_and_metadata(self):
        comment_size = 60
        self._comment = [
            self._file_contents[self._position:
                                self._position + comment_size
                                ].decode('utf-8').replace('\x00', '').strip()]
        self._position += comment_size

        str_num = 20
        str_size = 12
        strings = []
        for _ in range(str_num):
            strings.append(self._file_contents[
                           self._position:
                           self._position + str_size].decode(
                'utf-8').replace('\x00', '').strip())
            self._position += str_size

        if self._file_format == 'ESR2':
            for _ in range(2):
                self._comment.append(
                    self._file_contents[self._position:
                                        self._position + comment_size
                                        ].decode('utf-8').replace('\x00',
                                                                  '').strip())
                self._position += comment_size

        # Only those metadata of interest are mapped
        # Note: The first nine parameters are input MANUALLY, never trust em.
        self._metadata = {
            "modulation_amplitude": strings[1],
            "modulation_frequency": strings[2],
            "time_constant": strings[3],
            "receiver_gain": float(strings[4]),
            "mw_power": strings[7],
            "mw_frequency": strings[8],
            "date": strings[9],
            "time": strings[10],
            "n_scans": int(strings[12]),
            "temperature": strings[13],
        }

    def _create_axis(self):
        self._parameters['start'] = \
            self._parameters['center_field'] \
            - self._parameters['sweep_width'] / 2
        self._parameters['stop'] = \
            self._parameters['center_field'] \
            + self._parameters['sweep_width'] / 2
        axis = np.linspace(self._parameters['start'],
                           self._parameters['stop'],
                           num=self._parameters['n_points'])
        self.dataset.data.axes[0].values = axis
        self.dataset.data.axes[0].unit = 'mT'

    def _assign_comment(self):
        comment_annotation = aspecd.annotation.Comment()
        comment_annotation.comment = self._comment
        self.dataset.annotate(comment_annotation)

    def _assign_metadata(self):
        self.dataset.metadata.magnetic_field.start.value = \
            self.dataset.data.axes[0].values[0]
        self.dataset.metadata.magnetic_field.stop.value = \
            self.dataset.data.axes[0].values[-1]
        self.dataset.metadata.magnetic_field.sweep_width.value = \
            self._parameters["sweep_width"]
        self.dataset.metadata.magnetic_field.start.unit = \
            self.dataset.metadata.magnetic_field.stop.unit = \
            self.dataset.metadata.magnetic_field.sweep_width.unit = "mT"
        self.dataset.metadata.signal_channel.accumulations = \
            self._metadata["n_scans"]


class NIEHSExpImporter(aspecd.io.DatasetImporter):
    """
    Importer for NIEHS PEST exp (text) files.

    The text file format dealt with here is actually a series of different
    formats, just to make life easier. The most basic format simply
    contains (usually two) columns with numerical data, but there are
    other versions as well with additional information on top.

    In case of the latter format with additional information on top of the
    file, this information is added as comment annotation to the dataset.

    For details of the file format, see the section :ref:`exp_format`.

    .. note::
        Due to the lack of any metadata of this format, the resulting
        dataset is quite limited in its metadata. Only the axes measures
        and units are added (by informed guessing). Therefore, you are
        highly encouraged to provide the lacking metadata by other means.


    .. versionadded:: 0.3

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self._file_contents = None
        self._lines = None
        self._file_format = None
        self._raw_data = None
        self._header = None

    def _import(self):
        self._clean_filenames()
        self._read_file_contents()
        self._detect_file_format()
        self._import_data()
        self._assign_data_and_axis()
        self._assign_comment()

    def _clean_filenames(self):
        # Dirty fix: Cut file extension
        if self.source.endswith(".exp"):
            self.source = self.source[:-4]

    def _read_file_contents(self):
        filename = self.source + ".exp"
        with open(filename, 'r') as file:
            self._file_contents = file.read()
        self._lines = self._file_contents.splitlines()

    def _detect_file_format(self):
        if self._lines[0].startswith('['):
            self._file_format = 'with_blocks'
        else:
            self._file_format = 'DSV'

    def _import_data(self):
        if self._file_format == 'with_blocks':
            # noinspection PyTypeChecker
            self._raw_data = np.loadtxt(
                io.StringIO(self._file_contents),
                skiprows=self._lines.index('[DATA]') + 1)
            self._header = self._lines[:self._lines.index('[DATA]')]
        else:
            # noinspection PyTypeChecker
            self._raw_data = np.loadtxt(io.StringIO(self._file_contents))

    def _assign_data_and_axis(self):
        self.dataset.data.axes[0].values = self._raw_data[:, 0] / 10
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.data = self._raw_data[:, 1]

    def _assign_comment(self):
        if self._header:
            # Remove empty lines and trailing spaces
            self._header = [element.rstrip() for element in self._header
                            if element != '']
            comment_annotation = aspecd.annotation.Comment()
            comment_annotation.comment = self._header
            self.dataset.annotate(comment_annotation)
