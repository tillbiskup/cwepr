import datetime
import os
import struct
import unittest

import numpy as np

import cwepr.dataset
import cwepr.io

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestESPWinEPRImporter(unittest.TestCase):
    def setUp(self):
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.sources = [
            os.path.join(ROOTPATH, path)
            for path in [
                "testdata/ESP",
                "testdata/EMX-winEPR.par",
                "testdata/winepr.par",
            ]
        ]
        self.source = os.path.join(ROOTPATH, "testdata/winepr.par")
        self.par_filename = "delete_me.par"
        self.spc_filename = "delete_me.spc"

    def tearDown(self):
        if os.path.exists(self.par_filename):
            os.remove(self.par_filename)
        if os.path.exists(self.spc_filename):
            os.remove(self.spc_filename)

    def write_spc_file(self, n_points=1024, format="WinEPR"):
        if format == "WinEPR":
            data = np.random.random(n_points)
            encoding = "<f"
        else:
            data = np.random.randint(2**10, size=n_points)
            encoding = ">i"
        with open(self.spc_filename, "wb") as file:
            for number in range(data.size):
                file.write(struct.pack(encoding, data[number]))
        return data

    def write_par_file(self, contents=None):
        with open(self.par_filename, "w", encoding="utf8") as file:
            for key, value in contents.items():
                file.write(f"{key} {value}\n")

    def test_imports_esp_data_correctly(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[0]
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.data[0] < 10**12)

    def test_imports_winepr_data_correctly(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[1]
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.data[0] < 10**12)

    def test_importing_esp_data_sets_type_parameter(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[0]
        self.dataset.import_from(importer)
        self.assertEqual("ESP", importer.parameters["format"])

    def test_importing_winepr_data_sets_type_parameter(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[1]
        self.dataset.import_from(importer)
        self.assertEqual("WinEPR", importer.parameters["format"])

    def test_type_parameter_overrides_automatic_format_detection(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[0]
        importer.parameters["format"] = "WinEPR"
        self.dataset.import_from(importer)
        self.assertEqual("WinEPR", importer.parameters["format"])

    def test_type_parameter_overrides_automatic_format_detection_2(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(
            source=self.sources[1]
        )
        importer.parameters["format"] = "ESP"
        self.dataset.import_from(importer)
        self.assertEqual("ESP", importer.parameters["format"])

    def test_gets_parameter(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[0]
        self.dataset.import_from(importer)
        self.assertTrue(len(importer._par_dict.keys()) > 1)

    def test_infofile_gets_imported(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[0]
        self.dataset.import_from(importer)
        self.assertTrue(
            isinstance(self.dataset.metadata.bridge.mw_frequency.value, float)
        )

    def test_map_par_parameters_correctly(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[0]
        self.dataset.import_from(importer)
        self.assertEqual(
            5.000000e05,
            self.dataset.metadata.signal_channel.receiver_gain.value,
        )
        self.assertAlmostEqual(
            339.498, self.dataset.metadata.magnetic_field.start.value, 2
        )

    def test_map_par_parameters_correctly_second_dataset(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[1]
        self.dataset.import_from(importer)
        self.assertAlmostEqual(
            350.5, self.dataset.metadata.magnetic_field.start.value, 2
        )

    def test_import_with_1D_dataset(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.axes[0].unit in ("G", "mT"))
        self.assertFalse(self.dataset.data.axes[1].unit)

    def test_winepr_sets_default_values(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[2]
        self.dataset.import_from(importer)
        self.assertEqual(
            100,
            self.dataset.metadata.signal_channel.modulation_frequency.value,
        )
        self.assertEqual(
            "kHz",
            self.dataset.metadata.signal_channel.modulation_frequency.unit,
        )

    def test_time_gets_imported_correctly_from_par(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[2]
        self.dataset.import_from(importer)
        date_time = datetime.datetime(2021, 10, 15, 10, 37)
        self.assertEqual(date_time, self.dataset.metadata.measurement.start)

    def test_frequency_gets_written(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[2]
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.metadata.bridge.mw_frequency.value)

    def test_operator_is_written_from_infofile(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[1]
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.metadata.measurement.operator)
        self.assertTrue(self.dataset.metadata.measurement.purpose)
        self.assertTrue(self.dataset.metadata.experiment.type)
        self.assertTrue(self.dataset.metadata.probehead.type)
        self.assertTrue(
            self.dataset.metadata.temperature_control.temperature.value
        )

    def test_mod_amp_has_unit(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.sources[1]
        self.dataset.import_from(importer)
        self.assertEqual(
            self.dataset.metadata.signal_channel.modulation_amplitude.unit,
            "G",
        )

    def test_creating_spc_file(self):
        data = self.write_spc_file()
        np.testing.assert_allclose(data, np.fromfile(self.spc_filename, "<f"))
        data = self.write_spc_file(format="ESP")
        np.testing.assert_allclose(
            data, np.fromfile(self.spc_filename, ">i4")
        )

    def test_creating_par_file(self):
        params = {"DOS": "Format", "RES": "2048"}
        self.write_par_file(params)

    def test_read_winepr_power_sweep(self):
        params = {
            "DOS": "Format",
            "SSX": "1024",
            "SSY": "5",
            "XXLB": "3400.000000",
            "XXWI": "200.000000",
            "XYLB": "0.000000",
            "XYWI": "4.000000",
            "XXUN": "G",
            "XYUN": "dB",
            "JEX": "field-sweep",
            "JEY": "mw-power-sweep",
            "REY": "5",
            "JDA": "10/15/2021",
            "JTM": "10:37",
            "MP": "2.012e-001",
            "MPS": "-5.000e+000",
        }
        self.write_par_file(params)
        self.write_spc_file(n_points=5 * 1024)
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter()
        importer.source = self.par_filename
        self.dataset.import_from(importer)
        self.assertListEqual([1024, 5], list(self.dataset.data.data.shape))
        self.assertEqual(340, self.dataset.data.axes[0].values[0])
        # NOTE: This axis should be in mW, not in dB
        np.testing.assert_allclose(
            np.asarray([0.2012, 0.63625, 2.012, 6.3625, 20.12]),
            self.dataset.data.axes[1].values,
            rtol=1e-2,
        )
        self.assertEqual(
            "microwave power", self.dataset.data.axes[1].quantity
        )
        self.assertEqual("mW", self.dataset.data.axes[1].unit)
