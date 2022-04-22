from .loader import LoadedData


class DatasetCreator:
    def __init__(self, data: LoadedData,
                 enable_parent_nodes: bool = False,
                 enable_input_in_output: bool = False):
        '''
        transforms the `LoadedData` based on the flags provided:

        `enable_parent_nodes`: activates all parent nodes in the inputs and outputs
        `enable_input_in_output`: adds the input nodes to the output set
        '''
        self.hpo = data.hpo
        self._subjects: list[tuple[set[str], set[str]]] = []
        'for each subject a tuple (labevents, diagnoses)'

        for subject in data.subjects.values():
            labevents = subject.labevents.copy()
            diagnoses = subject.diagnoses.copy()
            if enable_parent_nodes:
                self._add_all_parents_to_set(labevents)
                self._add_all_parents_to_set(diagnoses)
            if enable_input_in_output:
                diagnoses.update(labevents)
            self._subjects.append((labevents, diagnoses))

        # calculate all hpo features used
        all_present_hpo_features: set[str] = set()
        for subject in self._subjects:
            all_present_hpo_features.update(subject[0])
            all_present_hpo_features.update(subject[1])
        self.feature_list = [e for e in all_present_hpo_features]

    def _add_all_parents_to_set(self, s: set[str]):
        original_features = [e for e in s]
        for feature in original_features:
            self.hpo.entries_by_id[feature].add_all_parents(s)

    def one_hot_encoding(self, features: set[str]) -> list[int]:
        return [int(feature in features) for feature in self.feature_list]

    def input_data_one_hot(self) -> list[list[int]]:
        return [self.one_hot_encoding(subject[0]) for subject in self._subjects]

    def target_data_one_hot(self) -> list[list[int]]:
        return [self.one_hot_encoding(subject[0]) for subject in self._subjects]
