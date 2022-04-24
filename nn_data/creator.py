from typing import Iterable, Literal
from utils.hpo import HPO
from .loader import LoadedData


def _one_hot_encoding(feature_list: list[str], features: set[str]) -> list[int]:
    return [int(feature in features) for feature in feature_list]


def _add_upwards_to_set(hpo: HPO, features: Iterable[str], s: set[str]):
    'adds all parants of features to s'
    for feature in features:
        hpo.entries_by_id[feature].add_all_parents(s)


class DatasetCreator:
    '''Creates data for model training based on an `LoadedData` object
    '''

    def __init__(self, data: LoadedData):
        self.hpo = data.hpo
        self._subjects: dict[int, set[str]] = {}
        self.feature_list: list[str]
        'for each subject a tuple (labevents, diagnoses)'

    def _compute_feature_list(self):
        all_present_features: set[str] = set()
        for features in self._subjects.values():
            all_present_features.update(features)
        self.feature_list = [e for e in all_present_features]

    def data(self) -> list[list[int]]:
        'data for model training'
        return [_one_hot_encoding(self.feature_list, features) for features in self._subjects.values()]

    def combine(self, outputs: list[int], targets: list[int]):
        assert len(self.feature_list) == len(outputs) == len(targets)
        return zip(self.feature_list, outputs, targets)


class HPODatasetCreator(DatasetCreator):
    '''Creates data for model training based on an `LoadedData` object
    '''

    def __init__(self, data: LoadedData,
                 mode: Literal['labevents', 'diagnoses'],
                 enable_parent_nodes: bool = False,
                 ):
        '''parameters:
        - `enable_parent_nodes`: activates all parent nodes in the inputs and outputs
        '''
        super().__init__(data)

        for subject_id, subject in data.subjects.items():
            if mode == 'labevents':
                activated_nodes: set[str] = subject.labevents_hpo.copy()
            else:
                activated_nodes: set[str] = subject.diagnoses_hpo.copy()

            features = activated_nodes.copy()
            if enable_parent_nodes:
                parents: set[str] = set()
                _add_upwards_to_set(self.hpo, activated_nodes, parents)
                features.update(parents)

            self._subjects[subject_id] = features

        self._compute_feature_list()


class ICDDatasetCreator(DatasetCreator):
    '''Creates data for model training based on an `LoadedData` object
    '''

    def __init__(self, data: LoadedData, batch: bool = False):
        '''parameters:
        - `batch`: uses only the first 3 characters from the ICD-code
        '''
        super().__init__(data)

        for subject_id, subject in data.subjects.items():
            features: set[str] = subject.diagnoses_icd.copy()
            if batch:
                features = {e[:3] for e in features}
            self._subjects[subject_id] = features

        self._compute_feature_list()
