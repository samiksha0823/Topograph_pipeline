"""
missing_link_healer.py
----------------
PHASE 2 of the "Ontology Healer" pipeline: "Heal"

Upgrades the original ad-hoc "top-k nearest pairs" missing-link search into
something defensible in front of judges, by tying it directly to the
persistent homology computation itself rather than a separate heuristic:

1. Pull every 1-simplex (i.e. every pair of nodes) the Rips filtration would
   ever connect, in the exact order it connects them (sorted by filtration
   value = semantic distance). This is the literal "topological merging
   order" the abstract refers to.
2. Walk that order and keep the pairs that are NOT already a declared
   cross-reference edge. These are nodes the semantic topology says
   "should" be close, that human curators never linked.
3. For each candidate, report defensible statistics a judge can check
   without trusting our framing:
     - percentile rank among all C(41,2)=820 possible pairs
     - z-score relative to the mean/std of all pairwise distances
     - whether the pair is even reachable via any chain of declared edges
       at all (same weakly-connected component) - if NOT reachable, that's
       the strongest possible curation-gap evidence
"""

import numpy as np


def get_filtration_ordered_pairs(simplex_tree, node_ids):
    """Returns all 1-simplices (node pairs) in the order the Rips filtration
    would introduce them, i.e. sorted by filtration value ascending."""
    pairs = []
    for simplex, filtration_value in simplex_tree.get_filtration():
        if len(simplex) == 2:
            i, j = simplex
            pairs.append((node_ids[i], node_ids[j], filtration_value))
    pairs.sort(key=lambda x: x[2])
    return pairs


def healed_missing_links(simplex_tree, node_ids, distance_matrix, declared_edges_undirected,
                          declared_graph, top_k=5):
    """Returns the top_k most statistically defensible missing-link candidates."""
    all_distances = distance_matrix[np.triu_indices_from(distance_matrix, k=1)]
    mean_d, std_d = all_distances.mean(), all_distances.std()
    sorted_distances = np.sort(all_distances)

    ordered_pairs = get_filtration_ordered_pairs(simplex_tree, node_ids)
    declared_set = {frozenset(e) for e in declared_edges_undirected}

    import networkx as nx
    components = {n: i for i, comp in enumerate(nx.weakly_connected_components(declared_graph)) for n in comp}

    candidates = []
    for a, b, d in ordered_pairs:
        if frozenset((a, b)) in declared_set:
            continue
        percentile = float(np.searchsorted(sorted_distances, d) / len(sorted_distances) * 100)
        z = (d - mean_d) / std_d if std_d > 0 else 0.0
        same_component = components.get(a) == components.get(b)
        candidates.append({
            "a": a, "b": b, "distance": round(float(d), 4),
            "percentile_rank": round(percentile, 2),
            "z_score": round(float(z), 2),
            "reachable_via_declared_chain": bool(same_component),
        })
        if len(candidates) >= top_k:
            break

    return candidates, {"mean_distance": round(float(mean_d), 4), "std_distance": round(float(std_d), 4),
                         "n_total_pairs": len(all_distances)}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from data_loader import load_experiential_knowledge, load_quality_metrics, load_cross_references
    from graph_builder import build_knowledge_graph
    from tda_analysis import build_text_corpus, semantic_distance_matrix, compute_persistence

    ek = load_experiential_knowledge("data/experiential_knowledge_41.json")
    _, per_entry, _ = load_quality_metrics("data/quality_metrics.json")
    edges, _ = load_cross_references("data/cross_references.json")
    G = build_knowledge_graph(ek, per_entry, edges)
    node_ids = [e["id"] for e in ek]

    corpus = build_text_corpus(ek)
    dist, vec, tfidf = semantic_distance_matrix(corpus)
    simplex_tree, persistence = compute_persistence(dist, max_edge_length=1.0, max_dimension=2)

    declared_undirected = [frozenset(e) for e in G.to_undirected().edges()]
    candidates, stats = healed_missing_links(simplex_tree, node_ids, dist, declared_undirected, G, top_k=5)

    print("Background stats:", stats)
    print("\nTop healed missing links (judge-checkable):")
    id_to_title = {e["id"]: e["title"] for e in ek}
    for c in candidates:
        print(f"  {c['a']} <-> {c['b']}  dist={c['distance']}  "
              f"percentile={c['percentile_rank']}%  z={c['z_score']}  "
              f"reachable_via_existing_chain={c['reachable_via_declared_chain']}")
        print(f"     \"{id_to_title[c['a']][:50]}\" <-> \"{id_to_title[c['b']][:50]}\"")
