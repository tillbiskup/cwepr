"""
Importer for the Bruker EMX and ESP format.

The Bruker EMX and ESP formats are used by older Bruker EPR spectrometers,
namely old EMX spectrometers running WinEPR and the ESP line of spectrometers.

A bit of a problem with these two formats is that they are quite similar,
but not the same. Namely the format of the file containing the data in
binary representation is completely different. The way to tell those
two formats apart is to import the ``.par`` file and look, if it contains
``DOS Format`` in the first line.

"""
import re

import aspecd.io
import aspecd.infofile
import numpy as np


class ESPWinEPRImporter(aspecd.io.DatasetImporter):
    def __init__(self, source=None):
        # Dirty fix: Cut file extension
        if source.endswith((".spc", ".par")):
            source = source[:-4]
        super().__init__(source=source)
        self.load_infofile = True
        # private properties
        self._infofile = aspecd.infofile.Infofile()
        self._par_dict = dict()
#        self._mapper_filename = 'dsc_keys.yaml'
#        self._is_two_dimensional = False
#        self._dimensions = []
        self._file_encoding = ''
#        self._points = int()

    def _import(self):
        self._read_parameter_file()
        self._import_data()

    def _import_data(self):
        complete_filename = self.source + '.spc'
        if ('DOS', 'Format') in self._par_dict.items():
            self._file_encoding = '<f'
        else:
            self._file_encoding = '>i4'
        raw_data = np.fromfile(complete_filename, self._file_encoding)
        self.dataset.data.data = raw_data

    def _read_parameter_file(self):
        par_filename = self.source + '.par'
        with open(par_filename, 'r') as file:
            lines = file.read().splitlines()

        for line in lines:
            line = line.split(maxsplit=1)
            key = line[0]
            if len(line) > 1:
                value = line[1]
            else:
                value = ''
            if re.match(r'^[+-]?[0-9.]+([eE][+-]?[0-9]*)?$', value):
                value = float(value)
            self._par_dict[key] = value


