"""Importer (Preparing raw data for processing)

This importer is used for raw data provided in the Bruker BES3T data format.
"""


import aspecd


class ImporterBES3T(aspecd.io.Importer):
    def __init__(self):
        super().__init__()

    def _import(self):
        pass

