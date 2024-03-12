"""
Importer for the Bruker EMX and ESP format.

The Bruker EMX and ESP formats are used by older Bruker EPR spectrometers,
namely old EMX spectrometers running WinEPR and the ESP (and ECS) series of
spectrometers.

A bit of a problem with these two formats is that they are quite similar,
but not the same. Namely the format of the file containing the data in
binary representation is completely different:

=====================  ===============================
Spectrometer           Binary encoding
=====================  ===============================
Bruker EMX / WinEPR    4 byte floating point
Bruker ESP (and ECS)   4 byte integer Motorola format
=====================  ===============================

One way to tell those two formats apart is to import the ``.par`` file and
look, if it contains ``DOS Format`` (or alternatively, ``ASCII Format``) in
the first line. However, this is just a workaround, as the official format
specification does *not* allow for any clear discrimination between the two.

Eventually, the proof of the pudding is the eating: graphical representation
of the imported data will immediately tell whether the importer chose the
correct format: Either way, the wrong interpretation of the binary data will
produce "garbage" a human can easily tell apart from an EPR spectrum (and
even if it only contained spectrometer noise). Hence, if something goes
wrong, you can explicitly provide the (correct) format to use. See the
documentation of the :class:`ESPWinEPRImporter` class for details.


Format documentation
====================

Generally, the format consists of two files per each measurement, a binary
spectrum file with ``spc`` extension (and different binary encoding,
as mentioned above) and an ASCII parameter file with ``par`` extension that
should be the same for both binary formats, technically speaking. However,
EMX spectrometers operated by WinEPR tend to add parameters to the parameter
file that are *not* described in the format specification, but *may* be used
to discriminate between EMX/WinEPR and ESP formats.

Just to make life simpler, a parameter file usually contains *only* those
parameters that deviate from what Bruker defined as "default" value. Those
default values are tabulated in the specification of the file format. A
particularly lovely quote from the specification, regarding defining the *x*
axis of your data:

    Definition of the x-axis can be very tricky because of instrument
    offsets, *etc.* To make sure that the x-axis is represented correctly,
    you should always use the parameters GST (start value) and GSI (sweep
    size) and do not use HCF (center field) and HSW (sweep width).

Following is the complete list of parameters, together with their default
values and their meaning, as given in the official specification:

======= ================ =========================================================
Keyword Default Value    Definition
======= ================ =========================================================
JSS     0                spectrum status word
JON                      operator name
JRE                      resonator name
JDA                      date of acquisition
JTM                      time of acquisition
JCO                      comment
JUN     Gauss            units (Gauss/Mhz/sec/...)
JNS     1                Scans to do
JSD     0                Scans done
JEX     EPR              Type of experiment
JAR     ADD              Mode (Add/Replace)
GST     3.455000e+03     left border of display
GSI     5.000000e+01     width of display
TE      -l.000000e+00    temperature (-1 means not set by software)
HCF     3.480006e+03     ER032M center field
HSW     5.000000e+01     ER032M sweep width
NGA     -1               ER035M gaussmeter address (-1 means not connected)
NOF     0.000000e+00     ER035M gaussmeter field offset
MF      -1.000000e+00    Microwave frequency (-1 means no input made)
MP      -1.000000e+00    Microwave power
MCA     -1               Microwave counter address (-1 means no counter connected)
RMA     1.000000e+00     ER023M modulation amplitude [Gauss]
RRG     2.000000e+04     ER023M receiver gain
RPH     0                ER023M phase
ROF     0                ER023M offset
RCT     5.120000e+00     ER023M conversion time
RTC     1.280000e+00     ER023M time constant
RMF     1.000000e+02     ER023M modulation frequency [kHz]
RHA     1                ER023M harmonic
RRE     1                ER023M resonator
RES     1024             resolution of ER023M spectra
DTM     4.096000e+00     digitizer sweep time [sec]
DSD     0.000000e+00     digitizer sweep delay [sec]
DCT     1000             digitizer conversion time [νsec]
DTR     1000             digitizer trigger rate
DCA     ON               channel A
DCB     OFF              channel B
DDM     OFF              DUAL mode
DRS     4096             digitizer resolution in x-axis
PPL     OFF              parameter plot
PFP     2                frame pen
PSP     1                spectra pen
POF     0                plot offset
PFR     ON               frame On/OFF
EMF     3.352100e+03     ENMR field
ESF     2.000000e+01     ENMR start frequency [MHz]
ESW     1.000000e+01     ENMR sweep width [MHz]
EFD     9.977000e+0l     FM-modulation [kHz]
EPF     1.000000e+01     ENMR pump frequency [MHz]
ESP     20               ENMR RF attenuator [dB]
EPP     63               ENMR pump power attenuator [dB]
EOP     0                ENMR total power attenuator [dB]
EPH     0                ENMR phase
FME                      filter method
FWI                      filter width
FOP     2                filter order of polynomial
FER     2.000000e+00     filter value 'alpha'
======= ================ =========================================================

Note that usually, only a rather small subset of all these possible values
are of relevance, particularly in case of the EMX spectrometer series only
capable of performing conventional cw-EPR spectroscopy. The ESP
spectrometer series, in contrast, could be equipped with both, pulsed and
ENDOR capabilities and is the predecessor of the modern ELEXSYS series.

Regarding the first parameter, ``JSS``, there is a bit more information
available that should be documented here for completeness as well:

.. code-block:: text

    JSS is a number indicating the status of the spectrum. It is a decimal
    number. The following describes what the numbers mean in hex:

    /* CSPS: current spectrum status                                           */
    #define s_DUAL 0x00000001L  /* current status : DUAL can change            */
    #define s_2D   0x00000002L  /* manipulated spectrum is 2D-spec.            */
    #define s_FT   0x00000004L  /* Fourier Transformation was done             */
    #define s_MAN0 0x00000008L  /* 'soft' manipulation were done               */
    #define s_MAN1 0x00000010L  /* 'hard' manipulation were done               */
    /* 'soft' manipulation: baseline correction, addition of constant values   */
    /* or spectrum fits, multiplication with constant values, phase correction */
    /* 'hard' manipulation: add. and mult. with extern data (other spectra..)  */
    /* zero function, smoothing op., expansion (only when fixed);              */
    /* org. information lost!!!                                                */
    #define s_PROT 0x00000020L  /* Protection flag: manip. not allowed         */
    #define s_VEPR 0x00000040L  /* VEPR spectrum                               */
    #define s_POW  0x00000080L  /* power spectrum                              */
    #define s_ABS  0x00000100L  /* absolute value spectrum                     */
    #define s_FTX  0x00000200L  /* Fourier Trans. in x-dir. of 2D-spectrum     */
    #define s_FTY  0x00000400L  /* FT in y-dir. of 2D-spectrum                 */
    /* s_FTX and s_FTY : FT on all slices off the spectrum; single slice: s_FT */
    #define s_POW2 0x00000800L  /* 2D power spectrum                           */
    #define s_ABS2 0x00001000L  /* 2D absolute value spectrum                  */


Module documentation
====================

"""
import glob
import os
import re
from collections import OrderedDict
from datetime import datetime, timedelta

import numpy as np

import aspecd.io
import aspecd.infofile
import aspecd.annotation
import aspecd.metadata
import aspecd.utils


class BrukerESPWinEPRDefaultParameterValues:
    """
    Default parameter values for Bruker ESP/WinEPR parameter files.

    Generally, the format consists of two files per each measurement,
    a binary spectrum file with ``spc`` extension (and different binary
    encoding, as mentioned above) and an ASCII parameter file with ``par``
    extension that should be the same for both binary formats, technically
    speaking. However, EMX spectrometers operated by WinEPR tend to add
    parameters to the parameter file that are *not* described in the
    format specification, but *may* be used to discriminate between
    EMX/WinEPR and ESP formats.

    Just to make life simpler, a parameter file usually contains *only*
    those parameters that deviate from what Bruker defined as "default"
    value. Those default values are tabulated in the specification of the
    file format and are represented by this class. They are used as
    basis in the :class:`ESPWinEPRImporter` and the values overwritten by
    the parameters actually read from the ``par`` file. Note that only
    those parameters necessary to interpret the data are actually used by
    the named importer.

    Attributes
    ----------
    parameters : :class:`dict`
        Default parameter values for Bruker ESP/WinEPR parameter files.

        Special care is taken to preserve the type of the individual
        values, particularly in case of numeric values (int or float).


    .. note::

        The list of parameters is definitely not complete, although it
        follows strictly the Bruker file format specification documented
        above. Particularly in case of two-dimensional experiments such as
        microwave power sweeps and kinetics (time) scans, additional fields
        are written that are not part of the specification, but crucial for
        a sensible interpretation of the data. Furthermore, the only
        (partly) reliable distinction between ESP and WinEPR formats is by
        additional fields in the latter as well not part of the format
        specification.

    """

    def __init__(self):
        self.parameters = {
            "JSS": 0,
            "JON": "",
            "JRE": "",
            "JDA": "",
            "JTM": "",
            "JCO": "",
            "JUN": "Gauss",
            "JNS": 1,
            "JSD": 0,
            "JEX": "EPR",
            "JAR": "ADD",
            "GST": 3.455e3,
            "GSI": 5e1,
            "TE": -1e0,
            "HCF": 3.480006e+3,
            "HSW": 5e1,
            "NGA": -1,
            "NOF": 0.0,
            "MF": -1.0,
            "MP": -1.0,
            "MCA": -1,
            "RMA": 1.0,
            "RRG": 2e4,
            "RPH": 0.0,
            "ROF": 0.0,
            "RCT": 5.12,
            "RTC": 1.28,
            "RMF": 1e2,
            "RHA": 1,
            "RRE": 1,
            "RES": 1024,
            "DTM": 4096.0,
            "DSD": 0.0,
            "DCT": 1000,
            "DTR": 1000,
            "DCA": "ON",
            "DCB": "OFF",
            "DDM": "OFF",
            "DRS": 4096,
            "PPL": "OFF",
            "PFP": 2,
            "PSP": 1,
            "POF": 0,
            "PFR": "ON",
            "EMF": 3.3521e3,
            "ESF": 2e1,
            "ESW": 1e1,
            "EFD": 9.977e1,
            "EPF": 1e1,
            "ESP": 20,
            "EPP": 63,
            "EOP": 0,
            "EPH": 0,
            "FME": "",
            "FWI": "",
            "FOP": 2,
            "FER": 2.0
        }


class ESPWinEPRImporter(aspecd.io.DatasetImporter):
    # noinspection PyUnresolvedReferences
    """
    Importer for the Bruker ESP and EMX formats.

    The Bruker EMX and ESP formats consist of two files, a data file with
    extension "spc" and a parameter file with extension "par". The
    particular problem with these two file formats is the different format
    of the binary data used. From the official specifications, there is no
    way to discriminate between ESP format (using Motorola format,
    translating to four-byte integer big endian), while the (old) EMX format
    (newer EMX machines probably use the BES3T format,
    see :class:`cwepr.io.BES3TImporter` for details) uses standard IEEE
    binary, translating to eight-byte float little endian.

    Furthermore, the parameter file usually contains only those values that
    deviate from the standard values given in the specification. Both are
    getting imported and the standard values overwritten by the differing
    values specified in the parameter file.


    Attributes
    ----------
    parameters : :class:`dict`
        Additional parameters to control import options.

        format : :class:`str`
            Identifier of the file format.

            Possible values are ``WinEPR``, ``ESP``, ``auto``

            Note: When setting the values explicitly before importing data,
            they are case-insensitive. But they will always be set to
            either of the two values shown above upon data import.

            There are two file formats in use with Bruker spectrometers
            that have (nearly) the same parameter files, but entirely
            different binary data files: The ESP and WinEPR (old EMX)
            formats, named after the respective spectrometer series.

            The importer does its best to automatically detect the format
            for you. However, as the official file format specification
            does not allow for such discrimination, these are necessarily
            informed guesses. Sometimes, you need to help the importer by
            explicitly stating which format you have at hand, Use this
            parameter in such cases.

            The parameter will be set after importing the data file,
            hence in retrospect you can always figure out which format has
            been detected.


    Examples
    --------
    Usually, you will use the importer implicitly when cooking a recipe.
    And in most cases, both, the overall file format as well as the
    special format (WinEPR or ESP) should be detected automatically for
    you. In such case, implicitly using the importer means just importing
    datasets:

    .. code-block:: yaml

        datasets:
          - winepr


    However, if you happen to have a dataset where the importer
    unfortunately fails with auto-detecting and discriminating between
    WinEPR and ESP formats, you may explicitly provide the format to use:

    .. code-block:: yaml

        datasets:
          - source: winepr
            importer: ESPWinEPRImporter
            importer_parameters:
              format: WinEPR

    For convenience, the format specifier is case-insensitive when set as
    parameter here. Note, however, that in the resulting history of the
    recipe, it is always written in the way specified above,
    see :attr:`parameters` for details.

    .. note::

        How do you know if the importer failed? Quite simple: Your
        resulting "spectrum" looks like garbage, but does not resemble an
        EPR spectrum at all. Typically, you will have sort of a step
        function with random oscillation between rather discrete values.

    If you want to explicitly tell the importer to auto-detect the format,
    *i.e.* discriminate between WinEPR and ESP formats -- that is the
    default behaviour anyway -- you may do something like this:

    .. code-block:: yaml

        datasets:
          - source: winepr
            importer: ESPWinEPRImporter
            importer_parameters:
              format: auto

    Just to mention: All examples so far have omitted the file extension.
    This is fine, as long as you do *not* have additional ASCII exports
    with the same file basename in the same directory, as in this case,
    the :class:`cwepr.io.factory.DatasetImporterFactory` will get confused.
    In such cases, you need to provide at least one of the two possible
    file extensions (``par``, ``spc``) explicitly:

    .. code-block:: yaml

        datasets:
          - winepr.par

    This would be equivalent to:

    .. code-block:: yaml

        datasets:
          - winepr.spc


    .. versionadded:: 0.2

    .. versionchanged:: 0.5.1
        Additional condition for WinEPR files; additional parameter ``format``

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self.parameters["format"] = "auto"
        self.load_infofile = True
        # private properties
        self._infofile = aspecd.infofile.Infofile()
        self._par_dict = BrukerESPWinEPRDefaultParameterValues().parameters
        self._mapper_filename = "par_keys.yaml"
        self._metadata_dict = OrderedDict()
        self._file_encoding = ""

    def _import(self):
        self._clean_filenames()
        self._read_parameter_file()
        self._import_data()

        if self.load_infofile and self._infofile_exists():
            self._load_infofile()
            self._map_infofile()

        self._map_par_file()
        self._set_metadata()
        self._get_number_of_points()
        self._ensure_common_units()
        self._fill_axes()

    def _clean_filenames(self):
        # Dirty fix: Cut file extension
        if self.source.endswith((".par", ".spc")):
            self.source = self.source[:-4]

    def _set_defaults(self):
        default_file = aspecd.utils.Yaml()
        default_file.read_stream(
            aspecd.utils.get_package_data(
                "cwepr@io/par_defaults.yaml"
            ).encode()
        )
        self._metadata_dict = default_file.dict

    def _read_parameter_file(self):
        par_filename = self.source + ".par"
        with open(par_filename, "r", encoding="ascii") as file:
            lines = file.read().splitlines()

        for line in lines:
            line = line.split(maxsplit=1)
            key = line[0]
            if len(line) > 1:
                value = line[1]
            else:
                value = ""
            if re.match(r"^[+-]?[0-9.]+([eE][+-]?[0-9]*)?$", value):
                value = float(value)
            self._par_dict[key] = value

    def _import_data(self):
        complete_filename = self.source + ".spc"
        self._get_file_encoding()
        raw_data = np.fromfile(complete_filename, self._file_encoding)
        self.dataset.data.data = raw_data

    def _get_file_encoding(self):
        if self.parameters["format"].lower() == "auto":
            if ("DOS", "Format") in self._par_dict.items() or (
                "ASCII",
                "Format",
            ) in self._par_dict.items():
                self.parameters["format"] = "WinEPR"
            else:
                self.parameters["format"] = "ESP"
        if self.parameters["format"].lower() == "winepr":
            self._file_encoding = "<f"
            self.parameters["format"] = "WinEPR"
        else:
            self._file_encoding = ">i4"
            self.parameters["format"] = "ESP"

    def _infofile_exists(self):
        if self._get_infofile_name() and os.path.exists(
            self._get_infofile_name()[0]
        ):
            return True
        print(
            f"No infofile found for dataset {os.path.split(self.source)[1]}, "
            f"import continued without infofile."
        )
        return False

    def _load_infofile(self):
        """Import infofile and parse it."""
        infofile_name = self._get_infofile_name()
        self._infofile.filename = infofile_name[0]
        self._infofile.parse()

    def _get_infofile_name(self):
        return glob.glob("".join([self.source.strip(), ".info"]))

    def _assign_comment_as_annotation(self):
        comment = aspecd.annotation.Comment()
        comment.comment = self._infofile.parameters["COMMENT"]
        self.dataset.annotate(comment)

    def _map_metadata(self, infofile_version):
        """Bring the metadata into a unified format."""
        mapper = aspecd.metadata.MetadataMapper()
        mapper.version = infofile_version
        mapper.metadata = self._infofile.parameters
        mapper.recipe_filename = "cwepr@metadata_mapper_cwepr.yaml"
        mapper.map()
        infofile_dict = aspecd.utils.convert_keys_to_variable_names(
            mapper.metadata
        )
        aspecd.utils.copy_keys_between_dicts(
            infofile_dict, self._metadata_dict
        )
        aspecd.utils.copy_values_between_dicts(
            infofile_dict, self._metadata_dict
        )

    def _map_infofile(self):
        """Bring the metadata to a given format."""
        infofile_version = self._infofile.infofile_info["version"]
        self._map_metadata(infofile_version)
        self._assign_comment_as_annotation()

    def _map_par_file(self):
        yaml_file = aspecd.utils.Yaml()
        yaml_file.read_stream(
            aspecd.utils.get_package_data(
                "cwepr@io/" + self._mapper_filename
            ).encode()
        )
        metadata_dict = {}
        metadata_dict = self._traverse(yaml_file.dict, metadata_dict)
        # metadata_dict = self._check_if_temperature_empty(metadata_dict)
        aspecd.utils.copy_keys_between_dicts(
            metadata_dict, self._metadata_dict
        )
        aspecd.utils.copy_values_between_dicts(
            metadata_dict, self._metadata_dict
        )
        self._extract_datetime()

    # TODO: Implement handling of "RT" in temperature value
    @staticmethod
    def _check_if_temperature_empty(metadata_dict):
        if (
            "value"
            not in metadata_dict["temperature_control"]["temperature"].keys()
            or metadata_dict["temperature_control"]["temperature"]["value"]
            == 0
        ):
            metadata_dict.pop("temperature_control")
        return metadata_dict

    def _extract_datetime(self):
        start_date = self._try_parsing_date()
        if "measurement" not in self._metadata_dict.keys():
            self._metadata_dict["measurement"] = {}
        self._metadata_dict["measurement"]["start"] = str(start_date)
        if "end" not in self._metadata_dict["measurement"].keys():
            self._metadata_dict["measurement"]["end"] = str(
                start_date + timedelta(minutes=1)
            )

    def _try_parsing_date(self):
        date = self._par_dict["JDA"] + " " + self._par_dict["JTM"]
        for fmt in ("%d-%b-%Y %H:%M:%S", "%d.%b.%Y %H:%M", "%m/%d/%Y %H:%M"):
            try:
                return datetime.strptime(date, fmt)
            except ValueError:
                pass
        raise ValueError("no valid date format found")

    def _set_metadata(self):
        self.dataset.metadata.from_dict(self._metadata_dict)

    def _traverse(self, dict_, metadata_dict):
        for key, value in dict_.items():
            if isinstance(value, dict):
                metadata_dict[key] = {}
                self._traverse(value, metadata_dict[key])
            elif value in self._par_dict.keys():
                metadata_dict[key] = self._par_dict[value]
            elif key == "specified_unit":
                metadata_dict["unit"] = value
        return metadata_dict

    def _ensure_common_units(self):
        """Transform selected values and units to common units.

        Because of information are doubled from the infofile and the
        par file, some units are wrong and are corrected manually here.
        """
        # microwave frequency
        if self.dataset.metadata.bridge.mw_frequency.value > 500:
            self.dataset.metadata.bridge.mw_frequency.value /= 1e9
        self.dataset.metadata.bridge.mw_frequency.unit = "GHz"
        # microwave power
        if self.dataset.metadata.bridge.power.value < 0.001:
            self.dataset.metadata.bridge.power.value *= 1e3
        self.dataset.metadata.bridge.power.unit = "mW"
        # magnetic field objects
        objects_ = ("start", "stop", "sweep_width")
        for object_ in objects_:
            magnetic_field_object = getattr(
                self.dataset.metadata.magnetic_field, object_
            )
            if magnetic_field_object.unit in ("Gauss", "G", ""):
                magnetic_field_object.value /= 10
                magnetic_field_object.unit = "mT"
            setattr(
                self.dataset.metadata.magnetic_field,
                object_,
                magnetic_field_object,
            )
        if not self.dataset.metadata.temperature_control.temperature.unit:
            self.dataset.metadata.temperature_control.temperature.unit = "K"

    def _fill_axes(self):
        self._get_magnetic_field_axis()
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = (
            self.dataset.metadata.magnetic_field.start.unit
        )
        self.dataset.data.axes[-1].quantity = "intensity"

    def _get_magnetic_field_axis(self):
        # Abbreviations:
        start = self.dataset.metadata.magnetic_field.start.value
        points = int(self.dataset.metadata.magnetic_field.points)
        sweep_width = self.dataset.metadata.magnetic_field.sweep_width.value
        #-# print("Start:", start, "Points: ", points, "SW:", sweep_width)
        # in WinEPR, Bruker takes the number of points correctly (in contrast
        # to other formats...)
        stop = start + sweep_width
        # Set axis
        magnetic_field_axis = np.linspace(start, stop, points)
        assert (
            len(magnetic_field_axis) == points
        ), "Length of magnetic field and number of points differ"
        assert (
            len(magnetic_field_axis) == self.dataset.data.data.shape[0]
        ), "Length of magnetic field and size of data differ"
        # set more values in dataset
        self.dataset.metadata.magnetic_field.stop.value = stop
        self.dataset.metadata.magnetic_field.stop.unit = (
            self.dataset.metadata.magnetic_field.start.unit
        )

        self.dataset.data.axes[0].values = magnetic_field_axis

    def _get_number_of_points(self):
        self.dataset.metadata.magnetic_field.points = len(
            self.dataset.data.data
        )
