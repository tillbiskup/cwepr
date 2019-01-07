import numpy as np


import aspecd.analysis


class FieldCorrectionValueFinding(aspecd.analysis.AnalysisStep):
    """
    g(Lilif) = 2.002293 +- 0.000002
    Reference: Rev. Sci. Instrum. 1989, 60, 2949-2952.

    Mu(B) = 9.27401*10**(-24)
    Reference: Rev. Mod. Phys. 2016, 88, ?.

    h = 6.62607*10**(-34)
    Reference: Rev. Mod. Phys. 2016, 88, ?.
    """
    VALUE_G_LILIF = 2.002293
    VALUE_MuB = 9.27401*10**(-24)
    VALUE_H = 6.62607*10**(-34)

    def __init__(self, nu_value):
        super().__init__()
        self.nu_value = nu_value

    def _perform_task(self):
        self.get_field_correction_value()

    def get_field_correction_value(self):
        index_max = np.argmax(self.dataset.data.data[1, :])
        index_min = np.argmin(self.dataset.data.data[1, :])
        experimental_field = (self.dataset.data.data[0, index_max] - self.dataset.data.data[0, index_min])/2.0
        calcd_field = self.VALUE_H*self.nu_value/self.VALUE_G_LILIF/self.VALUE_MuB
        delta_b0 = calcd_field - experimental_field
        self.results["Delta_B0"] = delta_b0

