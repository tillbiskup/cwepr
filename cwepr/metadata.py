"""Metadata

Supplementary data for a dataset, i.e. everything that is not
part of the literal experimental results, such as identifier,
date of the experiment..."""


import aspecd.metadata


class DatasetMetadata(aspecd.metadata.Metadata):
    """Set of all metadata for a dataset object.

     Attributes
    ----------
    replaced_values : 'list'
        List of all parameters that were present in the user made
        info file but subsequently replaced with information from
        the device parameter file.

    """
    def __init__(self):
        super().__init__()
        self.replaced_values = []
