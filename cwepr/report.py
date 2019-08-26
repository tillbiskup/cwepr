"""Report implementation for cwepr module."""


import aspecd.report


class ReporterCWEPR(aspecd.report.LaTeXReporter):
    """Report implementation for cwepr module.

    This class is needed because recipes cannot load aspecd reporter classes
    when run with cwEPR.
    """

    def __init__(self):
        super().__init__()
