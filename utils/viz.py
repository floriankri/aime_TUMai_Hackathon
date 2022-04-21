from typing import Iterable, Optional
from graphviz import Digraph
from .hpo import HPOEntry, HPO


def make_graph_to_depth(node: HPOEntry, depth: int) -> Digraph:
    'returns a graphviz graph with all children of `node` up to a depth of `depth`'
    g = Digraph()
    _graph_to_depth(g, node, depth)
    return g


def safe_id(id: str):
    'replaces `:` with `_` since graphviz ids cannot contain `:`'
    return id.replace(':', '_')


def _add_node(g: Digraph, entry: HPOEntry, color: str = "white"):
    g.node(safe_id(entry.id),
           f'<{entry.id}<br/><FONT POINT-SIZE="8">{entry.name}</FONT>>', shape="box", style="filled", fillcolor=color)


def _graph_to_depth(g: Digraph, node: HPOEntry, depth: int):
    'adds `node` and all children of `node` up to a depth of `depth` to `g`'
    _add_node(g, node)
    if depth <= 0:
        return
    for child in node._children:
        _graph_to_depth(g, child, depth-1)
        g.edge(safe_id(node.id), safe_id(child.id))


def make_graph_2(hpo: HPO, labevents: Iterable[str], diagnoses: Iterable[str],
                 labevent_color: str = "green", diagnoses_color: str = "yellow") -> Digraph:
    'generates a graph displaying the labevents and diagnoses'
    g = Digraph()
    e: set[str] = set()  # a set to keep track of the nodes added already

    def _add_upwards(node: HPOEntry, color: Optional[str] = None):
        'adds `node` and all of its parents (if they are not in `e`)'
        assert node.id not in e
        if color:
            _add_node(g, node, color)
        else:
            _add_node(g, node)
        e.add(node.id)
        for parent in node._parents:
            if parent.id not in e:
                _add_upwards(parent)
            g.edge(safe_id(parent.id), safe_id(node.id))

    for id in labevents:
        _add_upwards(hpo.entries_by_id[id], labevent_color)
    for id in diagnoses:
        _add_upwards(hpo.entries_by_id[id], diagnoses_color)
    return g
