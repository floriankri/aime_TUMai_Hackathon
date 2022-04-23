from typing import Literal
from utils.hpo import HPO
from .loader import LoadedData


def _one_hot_encoding(feature_list: list[str], features: set[str]) -> list[int]:
    return [int(feature in features) for feature in feature_list]


def _add_all_parents_to_set(hpo: HPO, s: set[str]):
    original_features = [e for e in s]
    for feature in original_features:
        hpo.entries_by_id[feature].add_all_parents(s)


class DatasetCreator:
    def __init__(self, data: LoadedData):
        self.hpo = data.hpo
        self._subjects: list[set[str]] = []
        self.feature_list: list[str]
        'for each subject a tuple (labevents, diagnoses)'

        # for subject in data.subjects.values():
        #     labevents = subject.labevents_hpo.copy()
        #     diagnoses = subject.diagnoses_hpo.copy()
        #     if enable_parent_nodes:
        #         self._add_all_parents_to_set(labevents)
        #         self._add_all_parents_to_set(diagnoses)
        #     if enable_input_in_output:
        #         diagnoses.update(labevents)
        #     self._subjects.append((labevents, diagnoses))

        # calculate all hpo features used
    def compute_feature_list(self):
        all_present_features: set[str] = set()
        for features in self._subjects:
            all_present_features.update(features)
        self.feature_list = [e for e in all_present_features]

    def data(self) -> list[list[int]]:
        return [_one_hot_encoding(self.feature_list, features) for features in self._subjects]


class HPODatasetCreator(DatasetCreator):
    def __init__(self, data: LoadedData,
                 mode: Literal['labevents', 'diagnoses'],
                 enable_parent_nodes: bool = False,
                 ):
        '''
        transforms the `LoadedData` based on the flags provided:

        `enable_parent_nodes`: activates all parent nodes in the inputs and outputs
        '''
        super().__init__(data)

        for subject in data.subjects.values():
            if mode == 'labevents':
                features: set[str] = subject.labevents_hpo.copy()
            else:
                features: set[str] = subject.diagnoses_hpo.copy()
            if enable_parent_nodes:
                _add_all_parents_to_set(self.hpo, features)
            self._subjects.append(features)

        self.compute_feature_list()
