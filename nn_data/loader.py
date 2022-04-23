from typing import Iterable
import utils
import pandas as pd


class Subject:
    def __init__(self, id):
        self.id = id
        self.labevents_hpo: set[str] = set()
        self.diagnoses_hpo: set[str] = set()
        self.diagnoses_icd: set[str] = set()

    def __repr__(self) -> str:
        return f'<Subject {self.id}>'


class LoadedData:
    def __init__(self, hpo_path: str, labevents_hpo_path: str, diagnoses_hpo_path: str,
                 labevents_hpo_column_name: str = 'selected_hpo_features',
                 diagnoses_hpo_column_name: str = 'hpo_features',
                 diagnoses_icd_column_name: str = 'icd9_code',
                 ):
        '''
        Loads the Human Phenotype Ontology, as well as the annotated labevents and diagnoses files.
        Groups the labevents and diagnoses data by subject id.
        '''
        self.hpo = utils.read_hpo_from_obo(hpo_path)
        labevents_df = pd.read_csv(labevents_hpo_path).fillna('')
        diagnoses_df = pd.read_csv(diagnoses_hpo_path).fillna('')

        self.subjects: dict[int, Subject] = {}

        for _, line in labevents_df.iterrows():
            subject_id = line.subject_id
            hpo_features = self.convert_hpo_to_proper_id(
                line[labevents_hpo_column_name].split(';'))
            subject = self.subjects.setdefault(subject_id, Subject(subject_id))
            subject.labevents_hpo.update(hpo_features)

        for _, line in diagnoses_df.iterrows():
            subject_id = line.subject_id
            hpo_features = self.convert_hpo_to_proper_id(
                line[diagnoses_hpo_column_name].split(';'))
            icd_features = line[diagnoses_icd_column_name].split(';')
            subject = self.subjects.setdefault(subject_id, Subject(subject_id))
            subject.diagnoses_hpo.update(hpo_features)
            subject.diagnoses_icd.update(icd_features)

    def convert_hpo_to_proper_id(self, s: Iterable[str]):
        # change alt ids to the main id
        return {self.hpo.proper_id[e] for e in s if e != ''}
