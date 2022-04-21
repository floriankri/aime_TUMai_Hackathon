class HPOEntry:
    'represents an entry of the human phenotype ontology.'

    def __init__(self,
                 id: str, name: str,
                 other_tags: dict[str, list[str]]):
        self.id = id
        'the ID of the entry. example: "HP:0000118"'
        self.name = name
        'the name of the entry example "Phenotypic abnormality"'
        self.other_tags = other_tags
        'contains all the data for this entry from the .obo file we do not (yet) care about'

        self._parents: list[HPOEntry] = []
        self._children: list[HPOEntry] = []

    def add_parent(self, parent: "HPOEntry"):
        assert self not in parent._children and parent not in self._parents
        self._parents.append(parent)
        parent._children.append(self)

    def __repr__(self) -> str:
        return f'<Entry {self.id} "{self.name}">'


entry_with_parent_ids = tuple[HPOEntry, list[str]]
'type alias: (entry, parent_ids)'


class HPO:
    'contains the human phenotype ontology'

    def __init__(self, entries: list[entry_with_parent_ids]):
        '''
        entries: all entries found in the .obo file along with their parent_ids.
        They will be connected 
        '''
        self.entries_by_id = {e[0].id: e[0] for e in entries}
        roots = []  # collect all the entries without a parent. There should be exactly one: the root
        for entry, parent_ids in entries:
            if len(parent_ids) == 0:
                roots.append(entry)
            for parent_id in parent_ids:
                entry.add_parent(self.entries_by_id[parent_id])
        assert len(
            roots) == 1, f'{len(roots)} entries with 0 parents found: {roots}'
        self.root = roots[0]
