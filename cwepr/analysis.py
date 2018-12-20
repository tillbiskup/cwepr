import numpy as np


import aspecd.analysis


class FieldCorrectionValueFinding(aspecd.analysis.AnalysisStep):
    def __init__(self):
        super().__init__()

    def analyse(self, dataset=None):
        if not self.dataset:
            if not dataset:
                raise aspecd.analysis.MissingDatasetError
            else:
                self.dataset = dataset
        self.get_field_correction_value(dataset)

    def get_field_correction_value(self, dataset):
        index_max = np.argmax(self.dataset.data.data[1, :])
        index_min = np.argmin(self.dataset.data.data[1, :])
        delta_b0 = self.dataset.data.data[0, index_max] - self.dataset.data.data[0, index_min]
        self.results["Delta_B0"] = delta_b0
        dataset.set_b0(delta_b0)
