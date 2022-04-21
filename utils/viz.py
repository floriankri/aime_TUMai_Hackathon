from graphviz import Digraph
from .hpo import HPO, HPOEntry


def make_graph_to_depth(node: HPOEntry, depth: int) -> Digraph:
    g = Digraph()
    _graph_to_depth(g, node, depth)
    return g


def safe_id(id: str): return id.replace(':', '_')


def _add_node(g: Digraph, entry: HPOEntry):
    g.node(safe_id(entry.id),
           f'<{entry.id}<br/><FONT POINT-SIZE="8">{entry.name}</FONT>>', shape="box")


def _graph_to_depth(g: Digraph, node: HPOEntry, depth: int):
    _add_node(g, node)
    if depth <= 0:
        return
    for child in node._children:
        _graph_to_depth(g, child, depth-1)
        g.edge(safe_id(node.id), safe_id(child.id))
