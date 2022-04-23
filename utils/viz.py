from typing import Iterable, Optional
from graphviz import Digraph
from .hpo import HPOEntry, HPO

LINE_COLOR = '#065CED'
LABEVENTS_COLOR = '#DEEAFF'
DIAGNOSES_COLOR = '#3580FF'
DEFAULT_COLOR = '#D9D9D9'


def _graph() -> Digraph:
    return Digraph(
        graph_attr={'fontname': 'DM Sans', },
        node_attr={'fontname': 'DM Sans', 'shape': 'box',
                   'style': 'filled,rounded',
                   'penwidth': '0.0'},
        edge_attr={'color': LINE_COLOR},
    )


def make_graph_to_depth(node: HPOEntry, depth: int) -> Digraph:
    'returns a graphviz graph with all children of `node` up to a depth of `depth`'
    g = _graph()
    _graph_to_depth(g, node, depth)
    return g


def safe_id(id: str):
    'replaces `:` with `_` since graphviz ids cannot contain `:`'
    return id.replace(':', '_')


def _add_node(g: Digraph, entry: HPOEntry, color: str = DEFAULT_COLOR):
    g.node(safe_id(entry.id),
           f'<{entry.id}<br/><FONT POINT-SIZE="8">{entry.name}</FONT>>', fillcolor=color)


def _graph_to_depth(g: Digraph, node: HPOEntry, depth: int):
    'adds `node` and all children of `node` up to a depth of `depth` to `g`'
    _add_node(g, node)
    if depth <= 0:
        return
    for child in node._children:
        _graph_to_depth(g, child, depth-1)
        g.edge(safe_id(node.id), safe_id(child.id))


def make_graph_2(hpo: HPO, labevents: Iterable[str], diagnoses: Iterable[str]) -> Digraph:
    'generates a graph displaying the labevents and diagnoses'
    g = _graph()
    e: set[str] = set()  # a set to keep track of the nodes added already

    def _add_upwards(node: HPOEntry, color: Optional[str] = None):
        'adds `node` and all of its parents (if they are not in `e`)'
        if color:
            _add_node(g, node, color)
        else:
            _add_node(g, node)
        if node.id not in e:
            for parent in node._parents:
                if parent.id not in e:
                    _add_upwards(parent)
                g.edge(safe_id(parent.id), safe_id(node.id))
        e.add(node.id)

    for id in labevents:
        _add_upwards(hpo.entries_by_id[id], LABEVENTS_COLOR)
    for id in diagnoses:
        _add_upwards(hpo.entries_by_id[id], DIAGNOSES_COLOR)
    return g
