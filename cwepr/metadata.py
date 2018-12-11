"""Metadata

Supplementary data for a dataset, i.e. everything that is not
part of the literal experimental results, such as identifier,
date of the experiment..."""


import aspecd.metadata


class DatasetMetadata(aspecd.metadata.Metadata):
    """Set of all metadata for a dataset object."""

    def __init__(self):
        super().__init__()
