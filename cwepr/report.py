"""Report implementation for cwepr module.

.. note::
    The dataset can be given either as dataset in the properties of a recipe, or
    via the apply_to parameter. In the first case, the dataset can be accessed
    in the here implemented reporter class via ``self.dataset`` (and as an
    object), in the latter
    case indirectly via operating on the context-object ``self.context[
    'dataset']`` (and as a dict). The dataset has to be given explicitly
    while the dataset-context is applied implicitly. Therefore, here is
    applied the usage of the context that is a bit more complicated in
    operating but more intuitive to write in recipes.


.. note::
    Still in active developing and not fail safe and easy to use.
"""

import collections
import copy
import os

import aspecd.report
import aspecd.dataset

import cwepr.dataset


class ExperimentalDatasetLaTeXReporter(aspecd.report.LaTeXReporter):
    """Report implementation for cwepr module."""

    def __init__(self, template='', filename=''):
        super().__init__(template=template, filename=filename)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        # private properties
        self._metadata = dict()
        self._tasks = collections.OrderedDict()
        self._figure_name = dict()

    def create(self):
        """Perform all methods to generate a report."""
        self._prepare_metadata()
        self._get_tasks()
        self._get_figure_names()
        self._create_context()
        self.context = self._sanitise_context(self.context)
        super().create()

    def _prepare_metadata(self):
        self._metadata = self.context['dataset']['metadata']
        self._metadata['parameter'] = collections.OrderedDict()
        self._collect_experimental_parameters()

    def _collect_experimental_parameters(self):
        """Collect all the metadata keys."""
        for key in self._metadata.keys():
            if key not in ['sample', 'measurement', 'parameter']:
                self._metadata['parameter'][key] = \
                    self._metadata[key]

    def _get_tasks(self):
        for task in self.dataset.tasks:
            if task['kind'] in ('analysis', 'processing'):
                self._tasks[(getattr(task['task'],
                                     task['kind']).description)] = {
                    'Parameters': getattr(task['task'],
                                          task['kind']).parameters,
                    'Comment': getattr(task['task'], task['kind']).comment
                }

    def _get_tasks_recursively(self, dict_=None):
        """Gets tasks recursively.

        Is able to get all the tasks performed on an single dataset what is
        only possible thanks to *call by reference* of the history records (
        ?). The dataset initially containing all the data has to be given in
        the recipe explicitly.

        .. note::
            Currently not used

        .. note: :
            Currently, the order of the tasks is *not* preserved because of
            the recursive search and the third step appears before the
            second. Therefore rework this with a different method, probably
            an other *context* keyword in a recipe.

        """
        for task in dict_.tasks:
            if task['kind'] == 'annotation':
                continue
            if task['kind'] == 'analysis':
                if isinstance(task['task'].analysis.result,
                              aspecd.dataset.CalculatedDataset):
                    self._get_tasks_recursively(task['task'].analysis.result)

            self._tasks[(getattr(task['task'],
                                 task['kind']).description)] = {
                'Parameters': getattr(task['task'],
                                      task['kind']).parameters,
                'Comment': getattr(task['task'], task['kind']).comment,
            }

    def _create_context(self):
        """Create a dictionary containing all data to write the report."""
        self.context['TASKS'] = self._tasks
        self.context['METADATA'] = self._metadata
        self.context['FIGURENAMES'] = self.includes

    def _sanitise_context(self, dict_=None):
        """Removes corresponding keys to empty values from context."""
        tmp_dict = copy.deepcopy(dict_)
        for key, value in dict_.items():
            if key == 'dataset':
                continue
            if isinstance(value, (collections.OrderedDict, dict)):
                tmp_dict[key] = self._sanitise_context(value)
            elif not value:
                tmp_dict.pop(key)
        dict_ = tmp_dict
        return dict_

    def _get_figure_names(self):
        """Get the names of the figures used for the report."""
        for i in range(len(self.dataset.representations)):
            if self.dataset.representations[i].plot.description \
                    == '2D plot as scaled image.':
                self._figure_name['Figure2D'] = \
                    self.dataset.representations[i].plot.filename
            elif self.dataset.representations[i].plot.description \
                    == '1D line plot.':
                self._figure_name['Figure1D'] = \
                    self.dataset.representations[i].plot.filename
            else:
                pass


class PowerSweepAnalysisReporter(aspecd.report.LaTeXReporter):
    """Create report for power sweep analysis."""

    def __init__(self, template='', filename=''):
        super().__init__(template=template, filename=filename)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        # private properties
        self._metadata = dict()
        self._tasks = dict()

    def create(self):
        """Perform all methods to generate a report."""
        #TODO:
        # nicht auf das angegebene Datenset aus den Rezept-Properties
        # verlassen. Stattdessen das Dataset, das aus Apply_To in den Kontext
        # gebaut wird, verwenden.
        # Die Datensets aus dem Kontext soweit verhauen, dass sie (leicht?)
        # in Template einbaubar sind.
        # Passendes Template bauen.

        self._prepare_metadata()
        self._get_tasks()
        # TODO: Die Figures ggf aus der Liste rausholen und in ein dict packen?
        #self._get_figure_names()
        self._create_context()
        self.context = self._sanitise_context(self.context)
        super().create()

    def _prepare_metadata(self):
        self._metadata = self.context['dataset']['metadata']
        self._metadata['parameter'] = collections.OrderedDict()
        self._collect_experimental_parameters()

    def _collect_experimental_parameters(self):
        """Collect all the metadata keys."""
        for key in self._metadata.keys():
            if key not in ['sample', 'measurement', 'parameter']:
                self._metadata['parameter'][key] = \
                    self._metadata[key]

    def _create_context(self):
        """Create a dictionary containing all data to write the report."""
        self.context['TASKS'] = self._tasks
        self.context['METADATA'] = self._metadata
        self.context['FIGURENAMES'] = self.includes

    def _get_tasks(self):
        for task, _ in enumerate(self.context['dataset']['tasks']):
            task = self.context['dataset']['tasks'][task]
            if task['kind'] in ('analysis', 'processing'):
                self._tasks[task['task'][task['kind']]['description']] = {
                    'Parameters': task['task'][task['kind']]['parameters'],
                    'Comment': task['task'][task['kind']]['comment']
                }
        fit = self.context['FITTING']
        fit_coeffs = fit.metadata.calculation.parameters['coefficients']
        further_tasks = self.context['CALCDATA'].tasks
        self._tasks[further_tasks[0]['task'].analysis.description] = {
            'Parameters': str(fit_coeffs),
            'Comment': further_tasks[0]['task'].analysis.comment
        }

    def _sanitise_context(self, dict_=None):
        tmp_dict = copy.deepcopy(dict_)
        for key, value in dict_.items():
            if key == 'dataset':
                continue
            if isinstance(value, (collections.OrderedDict, dict)):
                tmp_dict[key] = self._sanitise_context(value)
            elif not value:
                tmp_dict.pop(key)
        dict_ = tmp_dict
        return dict_


class DokuwikiCaptionsReporter(aspecd.report.Reporter):
    """Write DokuWiki Captions.

    ..todo::
        Write Documentation

    """

    def __init__(self):
        self.filename = ''
        self.language = 'de'
        self.template = self._get_template()
        super().__init__(template=self.template, filename=self.filename)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        # private properties
        self._metadata = dict()
        self._figure_name = dict()

    def create(self):
        """Perform all methods to create the captions."""
        self._prepare_metadata()
        self._create_context()
        super().create()

    def _get_template(self):
        language = self.language
        module_rootpath = os.path.split(os.path.abspath(
            __file__))[0]
        return os.path.join(module_rootpath, 'templates', language,
                            'DokuwikiCaption.txt.jinja')

    def _prepare_metadata(self):
        self._metadata = self.context['dataset']['metadata']
        self._metadata['parameter'] = collections.OrderedDict()
        self._collect_experimental_parameters()

    def _collect_experimental_parameters(self):
        """Collect all the metadata keys."""
        for key in self._metadata.keys():
            if key not in ['sample', 'measurement', 'parameter']:
                self._metadata['parameter'][key] = \
                    self._metadata[key]

    def _create_context(self):
        self.context['METADATA'] = self._metadata
