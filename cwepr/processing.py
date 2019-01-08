import aspecd.processing


class FieldCorrection(aspecd.processing.ProcessingStep):
    def __init__(self, correction_value):
        super().__init__()
        self.parameters["correction_value"] = correction_value

    def _perform_task(self):
        for n in range(len(self.dataset.data.data[0, :])):
            round(self.parameters["correction_value"], 6)
            self.dataset.data.data[0, n] += self.parameters["correction_value"]


class FrequencyCorrection(aspecd.processing.ProcessingStep):
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

    def __init__(self, nu_given, nu_target):
        super().__init__()
        self.parameters["nu_given"] = nu_given
        self.parameters["nu_target"] = nu_target

    def _perform_task(self):
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] = self._transform_to_g(self.dataset.data.data[0, n])
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] = self._transform_to_b(self.dataset.data.data[0, n])

    def _transform_to_g(self, value):
        return self.VALUE_H*self.parameters["nu_given"]/self.VALUE_MuB/value

    def _transform_to_b(self, value):
        return self.VALUE_H * self.parameters["nu_target"] / self.VALUE_MuB / value


class BaselineCorrection(aspecd.processing.ProcessingStep):
    def __init__(self):
        super().__init__()

    def _perform_task(self):
        pass
