"""Reproduce RMD-NETWORKX-0001 (networkx relabel copy-flag invariance, #8093).

MR (copy-flag invariance): nx.relabel_nodes with a node-merging mapping must
give the same node attributes whether copy=True or copy=False; the copy flag is
a representation choice, not a semantic one. Violation: with mapping {1:4,2:4}
the surviving node 4 keeps {x:4,y:4} under copy=True but is overwritten to
{x:2,y:2} under copy=False. (A clean bijective relabel is fine on 3.4.2; the
defect needs a merging mapping.)
"""
import networkx as nx


def _fresh():
    G = nx.Graph()
    for i in range(5):
        G.add_node(i, x=i, y=i)
    return G


def reproduce():
    mapping = {1: 4, 2: 4}  # non-injective: nodes 1 and 2 merge into 4

    H = nx.relabel_nodes(_fresh(), mapping, copy=True)
    attrs_copy = dict(H.nodes[4])

    G_inplace = _fresh()
    nx.relabel_nodes(G_inplace, mapping, copy=False)
    attrs_inplace = dict(G_inplace.nodes[4])

    violated = attrs_copy != attrs_inplace

    return {
        "id": "RMD-NETWORKX-0001",
        "project": "networkx",
        "version": nx.__version__,
        "mr_family": "graph relabeling: copy-flag invariance (representation-invariance)",
        "source": "relabel_nodes(G, {1:4,2:4}, copy=True).nodes[4]",
        "transformed": "relabel_nodes(G, {1:4,2:4}, copy=False) then G.nodes[4]",
        "expected": f"copy=True/False agree; copy=True gives {attrs_copy}",
        "observed": f"copy=True={attrs_copy}; copy=False={attrs_inplace}",
        "reproduced": bool(violated),
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    print(json.dumps(reproduce(), indent=2))
