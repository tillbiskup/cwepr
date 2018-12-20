import aspecd.processing


class FieldCorrection(aspecd.processing.ProcessingStep):
    def __init__(self, correction_value):
        super().__init__()
        self.correction_value = correction_value

    def _perform_task(self):
        for n in range(len(self.dataset.data.data[0, :])):
            round(self.correction_value, 6)
            self.dataset.data.data[0, n] += self.correction_value
