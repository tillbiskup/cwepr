"""Dataset (Container for experimental data and respective metadata)"""


import collections as col
import numpy as np

import aspecd
import aspecd.metadata

import cwepr.io
import cwepr.metadata


class Dataset(aspecd.dataset.ExperimentalDataset):
    """Set of data uniting all relevant information.

    The unity of numerical and metadata is indispensable for the
    reproducibility of data and is possible by saving all information
    available for one set of measurement data in a single instance of
    this class.
    """

    mappings = [
        ["GENERAL", "combine_items", [["Date start", "Time start"],
                                      "Start", " "]],
        ["GENERAL", "combine_items", [["Date end", "Time end"],
                                      "End", " "]],
        ["", "rename_key", ["GENERAL", "measurement"]],
        ["", "rename_key", ["TEMPERATURE", "temperature_control"]]
    ]

    def __init__(self):
        super().__init__()
        self.metadata = cwepr.metadata.DatasetMetadata()

    def import_from_file(self, filename):
        """Import data and metadata for a given filename.

        The appropriate importer automatically checks whether
        data and metadata files exist, matching a single format

        Parameters
        ----------
        filename : :class:`str`
            Path including the filename but not the extension.

        """
        importer_factory = cwepr.io.ImporterFactoryEPR()
        importer = importer_factory.get_importer(source=filename)
        super().import_from(importer=importer)

    def modify_field_values(self):
        """Wrapper method to get all magnetic field data in desired form.

        Fills in all variables concerning the magnetic field as appropriate
        and transforms them from gauss to millitesla.
        """
        self.metadata.magnetic_field.calculate_values()
        self.metadata.magnetic_field.gauss_to_millitesla()

    def map_metadata_and_check_for_overrides(self, metadata):
        """Perform some operations to yield the final set of metadata.

        Modifies names of metadata information as necessary, combines
        data from the INFO file and the spectrometer parameter file and checks
        for possible overrides.

        Parameters
        ----------
        metadata: :class:`list`
            Loaded metadata to use. First entry: from infofile;
            Second entry: from spectrometer parameter file.

        """
        metadata_mapper = aspecd.metadata.MetadataMapper()
        metadata_mapper.metadata = metadata[0]
        metadata_mapper.mappings = self.mappings
        metadata_mapper.map()
        self.metadata.from_dict(metadata_mapper.metadata)
        param_data_mapped = metadata[1]
        for data_part in param_data_mapped:
            self.metadata.from_dict(data_part)
            self._check_for_override(metadata_mapper.metadata, data_part)

    def _check_for_override(self, data1, data2, name=""):
        """Check if metadata from info file is overridden by parameter file.

        Compare the keys in the info file dict with those in each part of the
        dsc/par file to find overrides. Any matching keys are considered to be
        overriden and a respective note is added to
        :attr:`cwepr.metadata.DatasetMetadata.metadata_modifications`.
        The method cascades through nested dicts returning a
        'path' of the potential overrides.
        E.g., when the key 'a' in the sub dict 'b' is found in both dicts the
        path will be '/b/a'.

        Parameters
        ----------
        data1 : :class:`dict`
            Original data.

        data2: :class:`dict`
            Data that is added to the original dict.

        name: :class:`str`
            Used in the cascade to keep track of the path. This should not
            be set to anything other than the default value.

        """
        toplevel = False
        for entry in list(data1.keys()):
            data1[entry.lower()] = data1.pop(entry)
        for entry in data1.keys():
            if isinstance(data1[entry], col.OrderedDict):
                toplevel = True
        for entry in data1.keys():
            if entry in data2.keys():
                if toplevel:
                    if name.split("/")[-1] != entry:
                        name = ""
                    name = name + "/" + entry
                    self._check_for_override(data1[entry], data2[entry],
                                             name=name)
                else:
                    self.metadata.metadata_modifications.append(
                        "Possible override @ " + name + "/" + entry + ".")

    @staticmethod
    def _import_metadata(importer=None):
        """Import metadata using a selected importer.

        The appropriate importer automatically checks whether
        data and metadata files exist, matching a single format

        Parameters
        ----------
        importer : :class:`cwepr.importers.ImporterEPRGeneral`
            Importer instance to use for the import.

        Raises
        ------
        MissingImporterError :
            Raised, when no importer is provided

        """
        if not importer:
            raise aspecd.dataset.MissingImporterError("No importer provided")
        return importer.import_metadata()

    def fill_axes(self):
        """Add an x axis to the data.

        The y (intensity) values (coming from the actual data file) are used as
        already present. The x (field) values are created from the field data
        in the metadata.

        Both sets are combined and transformed into a numpy array.
        """
        field_points = []
        for step_index in range(self.metadata.magnetic_field.step_count):
            field_points.append(self.metadata.magnetic_field.field_min.value +
                                self.metadata.magnetic_field.step_width.value
                                * step_index)
        field_data = np.array(field_points)
        self.data.axes[0].values = field_data
        self.data.axes[0].quantity = "magnetic field"
        self.data.axes[0].unit = "mT"
        self.data.axes[1].quantity = "intensity"


class DatasetFactory(aspecd.dataset.DatasetFactory):
    """Implementation of the dataset factory for recipe driven evaluation"""

    def __init__(self):
        super().__init__()
        self.importer_factory = cwepr.io.ImporterFactoryEPR()

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
        dataset : :class:`cwepr.dataset.Dataset`
            Dataset object for cwepr package

        """
        return cwepr.dataset.Dataset()
