"""
Importer for simple text and CSV files.

Despite its obvious limitations (normally no metadata, limited resolution,
large files) text or CSV files are an often-encountered exchange format and
can serve as an easy way to import data from otherwise not supported file
formats, as nearly every software to record data allows to export these data
as simple text or CSV files.

You may have a look as well at the importers provided by the ASpecD package
for similar situations, particularly :class:`aspecd.io.TxtImporter`.
"""

import aspecd.io


class TxtImporter(aspecd.io.TxtImporter):
    r"""
    Importer for text files with various delimiters and separators.

    Automatically detects the extension of a file. Therefore, the importer
    should be given explicitly in the recipe if it is different from ".txt".

    Due to the inherent lacking of metadata in text files despite their
    widespread use, the importer adds three values as metadata in order to
    get the axis label for the magnetic field axis correctly:

    * Unit of the first axis: mT

    * Quantity of the fist axis: magnetic field

    * Quantity of the second axis: intensity


    Attributes
    ----------
    parameters : :class:`dict`
        Parameters controlling the import

        skiprows : :class:`int`
            Number of rows to skip in text file (*e.g.*, header lines)

        delimiter : :class:`str`
            The string used to separate values.

            Default: None (meaning: whitespace)

        comments : :class:`str` | :class:`list`
            Characters or list of characters indicating the start of a comment.

            Default: #

        separator : :class:`str`
            Character used as decimal separator.

            Default: None (meaning: dot)


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of the
    recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below for
    how to make use of this class. The examples focus each on a single aspect.

    The most general and simple case, using only default values:

    .. code-block:: yaml

        datasets:
          - eprdata.txt

    However, you can control the import in quite some detail, with respect to
    delimiter, decimal separator, rows to skip from the top, and comment
    character. A full example setting each of these parameters may look as
    follows:

    .. code-block:: yaml

        datasets:
          - source: eprdata.txt
            importer_parameters:
                delimiter: '\t'
                separator: ','
                skiprows: 3
                comments: '%'

    Here, the delimiter between columns is the tabulator, the decimal
    separator the comma, the first three lines are skipped by default as well
    as every line starting with a percent character, as this is interpreted as
    comment.

    A frequent use case is importing simulations that were carried out with
    EasySpin. A MATLAB excerpt for saving the simulated spectrum might look
    as follows:


    .. code-block:: matlab

        [B_sim_iso, Spc_sim_iso] = garlic(Sys, Exp);

        data = [B_sim_iso', Spc_sim_iso'];
        writematrix(data, 'Simulated-spectrum')


    Read in the simulated spectrum with:

    .. code-block:: yaml

        datasets:
          - source: Simulated-spectrum.txt
            id: simulation
            importer: TxtImporter
            importer_parameters:
                delimiter: ','


    .. versionchanged:: 0.5
        Renamed from CsvImporter to TxtImporter and generalised handling of text
        files. Now inherits from :class:`aspecd.io.TxtImporter`.

    """

    def __init__(self, source=""):
        super().__init__(source=source)
        # public properties
        self.extension = ".txt"
        self.parameters["skiprows"] = 0
        self.parameters["delimiter"] = None
        self.parameters["comments"] = "#"
        self.parameters["separator"] = None

    def _import(self):
        self._get_extension()
        super()._import()
        self._create_metadata()

    def _get_extension(self):
        if "." in self.source:
            extension = self.source[self.source.rfind(".") :]
        else:
            extension = None
        if extension:
            self.extension = extension
            self.source = self.source[: self.source.rfind(".")]
        self.source += self.extension

    def _create_metadata(self):
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[1].quantity = "intensity"


class CsvImporter(TxtImporter):
    """
    Simple importer for csv files containing EPR data.

    The delimiter defaults to the comma, as the name implies, but you can
    set the delimiter as well as other parameters explicitly. See
    :class:`TxtImporter` for details.

    Due to the inherent lacking of metadata in text files despite their
    widespread use, the importer adds three values as metadata in order to
    get the axis label for the magnetic field axis correctly:

    * Unit of the first axis: mT

    * Quantity of the fist axis: magnetic field

    * Quantity of the second axis: intensity

    .. versionchanged:: 0.5
        Renamed from CsvImporter to TxtImporter and generalised handling of text
        files. Now inherits from :class:`TxtImporter`.

    """

    def __init__(self, source=""):
        super().__init__(source=source)
        # public properties
        self.extension = ".csv"
        self.parameters["delimiter"] = ","
