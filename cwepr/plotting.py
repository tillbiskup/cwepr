import aspecd
import matplotlib.pyplot as ppl


class PlotterForTesting(aspecd.plotting.SinglePlotter):
    def __init__(self, coeffs0, coeffs1, coeffs3):
        super().__init__()
        self.coeffs0 = coeffs0
        self.coeffs1 = coeffs1
        self.coeffs3 = coeffs3

    def _create_plot(self):
        data = self.parameters["data"]
        x = data[0, :]
        y = data[1, :]

        ppl.plot(x, y, label="spectrum")
        ppl.plot(x, self.coeffs0[0])
        ppl.plot(x, self.coeffs1[1]+x*self.coeffs1[0])
        ppl.plot(x, self.coeffs3[3] + x * self.coeffs3[2] + x**2*self.coeffs3[1] +x**3*self.coeffs3[0])

        ppl.legend()
        ppl.show()