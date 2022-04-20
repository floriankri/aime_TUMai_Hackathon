
from io import TextIOWrapper
from typing import Optional
from .hpo import HPO, HPOEntry, entry_with_parent_ids


def unescape_text(text: str):
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


def parse_tag_value_line(line: str):
    assert ': ' in line

    tag, rest = line.split(': ', 1)
    assert '\\' not in tag

    comment = ''
    if ' ! ' in line:
        rest, comment = rest.split(' ! ', 1)

    if ' {' in line:
        rest, _ = rest.split(' {', 1)
    return tag, rest, comment


def get_next_line_from_file(f: TextIOWrapper) -> Optional[str]:
    while True:
        line = f.readline()
        if line == '':
            return
        line = line[:-1]
        if line == '' or line.startswith('!'):
            continue
        return line


def build_entry_from_tags(tags: dict[str, list[str]]) -> Optional[entry_with_parent_ids]:
    assert len(tags['id']) == 1 and len(tags['name']) == 1
    id = tags.pop('id')[0]
    name = tags.pop('name')[0]
    # todo: maybe 'alt_id' and 'replaced_by' are interessting
    parent_ids = tags.pop('is_a')
    if 'is_obsolete' in tags:
        # is obsolete -> don't add
        return
    entry = HPOEntry(id, name, tags)
    return entry, parent_ids


def get_entries_from_file(f: TextIOWrapper) -> list[entry_with_parent_ids]:
    # parse header
    while True:
        line = get_next_line_from_file(f)
        if line is None:
            return []
        if line.startswith('['):
            break  # end of header found

    # list of entries with their parents to be connected later
    entries: list[entry_with_parent_ids] = []
    while True:
        assert line == '[Term]', "hp.obo contains only [Term] stanzas"

        tags = {'id': [], 'name': [], 'is_a': []}
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


def read_hpo_from_obo(path: str):
    with open(path) as f:
        entries = get_entries_from_file(f)
    return HPO(entries)
