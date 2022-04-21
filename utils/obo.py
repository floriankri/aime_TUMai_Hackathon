
from io import TextIOWrapper
from typing import Optional
from .hpo import HPO, HPOEntry, entry_with_parent_ids

# file format spec: http://owlcollab.github.io/oboformat/doc/GO.format.obo-1_2.html#S.1.5

# this function is not yet called. it would be used for definition or comment tags


def unescape_text(text: str):
    'transforms escaped characters back to their proper form.'
    res = ''
    escape = False
    for ch in text:
        if escape:
            if ch == 'n':
                res += '\n'
            elif ch == '"':
                res += '"'
            else:
                print(f'escape character {ch} not known')
            escape = False
        elif ch == '\\':
            escape = True
        else:
            res += ch
    return res


def parse_tag_value_line(line: str) -> tuple[str, str, str]:
    '''parse a line `<tag>: <value> {<trailing modifiers>} ! <comment>`.
    output is a tuple of `(<tag>, <value>, <comment>)`.

    Example: `is_a: HP:0006530 ! Abnormal pulmonary interstitial morphology`
    would become `("is_a", "HP:0006530", "Abnormal pulmonary interstitial morphology")`
    '''
    assert ': ' in line, f'"{line}" is not a tag: value line'

    tag, rest = line.split(': ', 1)
    assert '\\' not in tag, f'tag connot contain escape characters'

    comment = ''
    if ' ! ' in line:
        rest, comment = rest.split(' ! ', 1)

    # filter out trailing modifiers, as we don't care about them
    if ' {' in line:
        rest, _ = rest.split(' {', 1)
    return tag, rest, comment


def get_next_line_from_file(f: TextIOWrapper) -> Optional[str]:
    'reads a line from `f`. Skips empty lines and comments. Returns `None` on EOF'
    while True:
        line = f.readline()
        if line == '':
            return None
        line = line[:-1]
        if line == '' or line.startswith('!'):
            continue
        return line


def build_entry_from_tags(tags: dict[str, list[str]]) -> Optional[entry_with_parent_ids]:
    '''given all tags of one entry returns an `HPOEntry` and a list of all parent_ids.
    for entries marked with `is_obsolete`, returns `None`
    '''
    assert len(tags.get('id', [])) == 1 and len(tags.get('name', [])
                                                ) == 1, 'each entry must contain `id` and `name`'
    id = tags.pop('id', [])[0]
    name = tags.pop('name', [])[0]
    # todo: maybe 'alt_id' and 'replaced_by' are interessting
    parent_ids = tags.pop('is_a', [])
    if 'is_obsolete' in tags:
        # is obsolete -> do not add
        return None
    entry = HPOEntry(id, name, tags)
    return entry, parent_ids


def get_entries_from_file(f: TextIOWrapper) -> list[entry_with_parent_ids]:
    # parse header
    while True:
        line = get_next_line_from_file(f)
        if line is None:  # EOF found
            return []
        if line.startswith('['):  # reached first entry
            break

    # list of entries to be connected later
    entries: list[entry_with_parent_ids] = []
    while True:
        assert line == '[Term]', "hp.obo contains only [Term] stanzas"

        # store all the tags for this entry.
        # each tag can appear multiple times, so we need a list for each entry.
        tags = {}
        while True:
            line = get_next_line_from_file(f)
            if line is None:
                return entries
            if line.startswith('['):
                e = build_entry_from_tags(tags)
                if e:
                    entries.append(e)
                break  # next term found

            tag, value, _ = parse_tag_value_line(line)
            tags.setdefault(tag, []).append(value)


def read_hpo_from_obo(path: str) -> HPO:
    'reads the file at `path` and build the HPO graph from it'
    with open(path) as f:
        entries = get_entries_from_file(f)
    return HPO(entries)
