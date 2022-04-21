import pandas as pd  # used for reading, modifying and writing csv files
import tqdm  # used for making a progess bar

# Adapted from:
# to_hpo.py (Made by Alexander Weiss alexander.weiss@mail.de)

# see https://github.com/TheJacksonLaboratory/loinc2hpoAnnotation for explantion of annotation dataset


# string that identify positive or negative test outcomes
NEG = ['neg', '0-']
POS = ['pos', '1+', '2+', '3+']


def is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def add_hpo_information(
    labitems_path: str,
    labevents_path: str,
    anno_path: str,
    labevents_hpo_path: str,
):
    # variables to keep track of errors
    missing_annotation: set[str] = set()
    missing_loinc: set[str] = set()
    unknown_flags: set[str] = set()
    unknown_values: set[str] = set()

    # parse labitems and annotations

    itemid_to_loinc: dict[str, str] = {}  # former loinc_dict
    # contains loinc-code for each item
    labitems_df = pd.read_csv(labitems_path).fillna('')
    for _, line in labitems_df.iterrows():
        if line.loinc_code != '':
            itemid_to_loinc[line.itemid] = line.loinc_code
    del labitems_df

    # for each loinc code contains outcome to HPO mapping.
    loinc_to_hpo: dict[str, dict[str, str]] = {}
    # Example: `loinc_to_hpo['2345-7'] = {'L': 'HP:0001943', 'N': 'HP:0011015', 'H': 'HP:0003074'}`
    anno_df = pd.read_csv(anno_path, sep='\t').fillna('')
    for _, line in anno_df.iterrows():
        entry = loinc_to_hpo.setdefault(line.loincId, {})
        entry[line.outcome] = line.hpoTermId
    del anno_df

    # go through each entry in labevents

    labevents_df = pd.read_csv(labevents_path).fillna('')

    selected_hpo_features: list[str] = []
    not_selected_hpo_features: list[str] = []
    unknown_hpo_features: list[str] = []
    for _, line in tqdm.tqdm(labevents_df.iterrows(), total=76074):
        # info["lines"] += 1
        selected: list[str] = []
        not_selected: list[str] = []
        unassigned: dict[str, str] = {}

        if line.itemid not in itemid_to_loinc:
            missing_loinc.add(line.itemid)
        else:
            loinc_code = itemid_to_loinc[line.itemid]

            if loinc_code not in loinc_to_hpo:
                missing_annotation.add(loinc_code)
            else:
                annotation = loinc_to_hpo[loinc_code]
                unassigned = annotation.copy()
                if not type(line.value) is str:
                    print(line)
                    return
                value: str = line.value.lower()
                if value == '' or is_float(value):
                    # quantitative result
                    if line.flag == '':
                        # normal
                        if 'L' in unassigned:
                            not_selected.append(unassigned.pop('L'))
                        if 'N' in unassigned:
                            not_selected.append(unassigned.pop('N'))
                        if 'H' in unassigned:
                            not_selected.append(unassigned.pop('H'))
                    elif line.flag == 'abnormal':
                        # abnormal does not say anything about high or low
                        if 'N' in unassigned:
                            selected.append(unassigned.pop('N'))
                    else:
                        unknown_flags.add(line.flag)
                elif value in NEG or value in POS:
                    # ordinal result
                    if 'NEG' in unassigned and 'POS' in unassigned:
                        if value in POS:
                            selected.append(unassigned.pop('POS'))
                        else:  # value in NEG
                            not_selected.append(unassigned.pop('NEG'))
                else:
                    unknown_values.add(line.value)

        selected_hpo_features.append(";".join(selected))
        not_selected_hpo_features.append(";".join(not_selected))
        unknown_hpo_features.append(";".join(unassigned.values()))

    labevents_df['selected_hpo_features'] = selected_hpo_features
    labevents_df['not_selected_hpo_features'] = not_selected_hpo_features
    labevents_df['unknown_hpo_features'] = unknown_hpo_features
    labevents_df.to_csv(labevents_hpo_path)
    print(f'missing loinc id for {len(missing_loinc)} items')
    print(f'missing annoation for {len(missing_annotation)} loinc ids')
    print(f'{unknown_flags=}')
    print(f'{unknown_values=}')
