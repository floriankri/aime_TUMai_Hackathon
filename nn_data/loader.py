from typing import Iterable
import utils
import pandas as pd


class Subject:
    def __init__(self, id):
        self.id = id
        self.labevents: set[str] = set()
        self.diagnoses: set[str] = set()

    def __repr__(self) -> str:
        return f'<Subject {self.id}>'


class LoadedData:
    def __init__(self, hpo_path: str, labevents_hpo_path: str, diagnoses_hpo_path: str):
        self.hpo = utils.read_hpo_from_obo(hpo_path)
        labevents_df = pd.read_csv(labevents_hpo_path).fillna('')
        diagnoses_df = pd.read_csv(diagnoses_hpo_path).fillna('')

        self.subjects: dict[int, Subject] = {}

        for _, line in labevents_df.iterrows():
            subject_id = line.subject_id
            hpo_features = self.convert_to_proper_id(
                line.selected_hpo_features.split(';'))
            self.subjects \
                .setdefault(subject_id, Subject(subject_id)) \
                .labevents.update(hpo_features)

        for _, line in diagnoses_df.iterrows():
            subject_id = line.subject_id
            hpo_features = self.convert_to_proper_id(
                line.hpo_features.split(';'))
            self.subjects \
                .setdefault(subject_id, Subject(subject_id)) \
                .diagnoses.update(hpo_features)

    def convert_to_proper_id(self, s: Iterable[str]):
        # change alt ids to the main id
        return {self.hpo.proper_id[e] for e in s if e != ''}


def load_data(hpo_path: str, labevents_hpo_path: str, diagnoses_hpo_path: str) -> LoadedData:
    '''
    Loads the Human Phenotype Ontology, as well as the annotated labevents and diagnoses files.
    Groups the labevents and diagnoses data by subject id.
    '''
    return LoadedData(hpo_path, labevents_hpo_path, diagnoses_hpo_path)
