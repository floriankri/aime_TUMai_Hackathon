class HPOEntry:
    def __init__(self,
                 id: str, name: str,
                 other_tags: dict[str, list[str]]):
        self.id = id
        self.name = name
        self.other_tags = other_tags

        self._parents: list[HPOEntry] = []
        self._children: list[HPOEntry] = []

    def add_parent(self, parent: "HPOEntry"):
        assert self not in parent._children and parent not in self._parents
        self._parents.append(parent)
        parent._children.append(self)

    def __repr__(self) -> str:
        return f'<Entry {self.id} "{self.name}">'


entry_with_parent_ids = tuple[HPOEntry, list[str]]


class HPO:
    def __init__(self, entries: list[entry_with_parent_ids]):
        self.entries_by_id = {e[0].id: e[0] for e in entries}
        possible_roots = []
        for entry, parent_ids in entries:
            if len(parent_ids) == 0:
                possible_roots.append(entry)
            for parent_id in parent_ids:
                entry.add_parent(self.entries_by_id[parent_id])
        assert len(
            possible_roots) == 1, f'{len(possible_roots)} possible root entries found: {possible_roots}'
        self.root = possible_roots[0]
