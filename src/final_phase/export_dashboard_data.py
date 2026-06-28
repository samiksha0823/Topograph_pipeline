"""
export_dashboard_data.py
----------------
Runs the full TopoGraph pipeline and exports every number/coordinate the
interactive HTML dashboard needs into a single JSON file. Keeping this
separate from the dashboard itself means the dashboard stays a static,
self-contained HTML file (no server needed for the live demo) while still
being driven by the real, freshly-computed pipeline output.
"""

import json
import networkx as nx

from data_loader import load_experiential_knowledge, load_quality_metrics, load_cross_references
from graph_builder import build_knowledge_graph, graph_summary
from graph_analytics import fragmentation_report
from quality_filtered_tda import (
    build_quality_filtered_distance_matrix, prove_zero_beta1,
    compute_quality_filtered_persistence, quality_fragmentation_curve,
)
from tda_analysis import build_text_corpus, semantic_distance_matrix, compute_persistence, betti_curve
from missing_link_healer import healed_missing_links

CATEGORY_COLORS = {
    "chain_pattern": "#E07A5F",
    "signal_interpretation": "#3D405B",
    "tactical_priority": "#81B29A",
    "bypass_technique": "#F2CC8F",
    "pitfall": "#9B5DE5",
}


def main():
    ek = load_experiential_knowledge("data/experiential_knowledge_41.json")
    agg_quality, per_entry_quality, _ = load_quality_metrics("data/quality_metrics.json")
    ref_edges, _ = load_cross_references("data/cross_references.json")
    node_ids = [e["id"] for e in ek]
    id_to_title = {e["id"]: e["title"] for e in ek}

    G = build_knowledge_graph(ek, per_entry_quality, ref_edges)
    g_summary = graph_summary(G)
    frag = fragmentation_report(G)

    # ---- layout (shared across all graph views so before/after lines up) ----
    pos = nx.spring_layout(G, seed=42, k=0.9)

    nodes_export = []
    for n in G.nodes():
        nodes_export.append({
            "id": n,
            "title": G.nodes[n]["title"],
            "category": G.nodes[n]["category"],
            "pass_count": G.nodes[n]["pass_count"],
            "confidence": G.nodes[n]["confidence"],
            "in_degree": G.in_degree(n),
            "out_degree": G.out_degree(n),
            "x": float(pos[n][0]),
            "y": float(pos[n][1]),
        })
    declared_edges_export = []
    for u, v in G.edges():
        qu, qv = G.nodes[u]["pass_count"], G.nodes[v]["pass_count"]
        declared_edges_export.append({
            "source": u, "target": v,
            "quality_distance": round(1.0 - min(qu, qv) / 8.0, 4),
        })

    # ---- Phase 1: quality-filtered proof + curve ----
    proof = prove_zero_beta1(G)
    q_dist = build_quality_filtered_distance_matrix(G, node_ids)
    q_simplex_tree, q_persistence = compute_quality_filtered_persistence(q_dist)
    q_curve = quality_fragmentation_curve(q_simplex_tree, max_dim=1, n_steps=60, max_eps=1.0)

    # ---- Phase 2: semantic TDA + missing links ----
    corpus = build_text_corpus(ek)
    dist, vectorizer, tfidf = semantic_distance_matrix(corpus)
    simplex_tree, persistence = compute_persistence(dist, max_edge_length=1.0, max_dimension=2)
    betti_over_time = betti_curve(simplex_tree, max_dim=1, n_steps=80, max_eps=1.0)
    declared_undirected = [frozenset(e) for e in G.to_undirected().edges()]
    missing_links, link_stats = healed_missing_links(
        simplex_tree, node_ids, dist, declared_undirected, G, top_k=8
    )

    def persistence_to_dict(pers):
        out = {0: [], 1: [], 2: []}
        for dim, (b, d) in pers:
            death = d if d != float("inf") else None
            out.setdefault(dim, []).append([float(b), death])
        return out

    export = {
        "category_colors": CATEGORY_COLORS,
        "summary": {
            "n_entries": len(ek),
            "n_declared_edges": G.number_of_edges(),
            "n_total_ref_edges": len(ref_edges),
            "n_isolated": frag["n_isolated_nodes"],
            "n_components": frag["n_components"],
            "avg_pass_count": agg_quality.get("avg_composite"),
        },
        "nodes": nodes_export,
        "declared_edges": declared_edges_export,
        "phase1": {
            "proof": proof,
            "betti_curve": {
                "eps": [round(e, 4) for e, _ in q_curve[0]],
                "beta0": [b for _, b in q_curve[0]],
                "beta1": [b for _, b in q_curve.get(1, [(e, 0) for e, _ in q_curve[0]])],
            },
        },
        "phase2": {
            "persistence": persistence_to_dict(persistence),
            "betti_curve": {
                "eps": [round(e, 4) for e, _ in betti_over_time[0]],
                "beta0": [b for _, b in betti_over_time[0]],
                "beta1": [b for _, b in betti_over_time.get(1, [(e, 0) for e, _ in betti_over_time[0]])],
            },
            "link_stats": link_stats,
            "missing_links": [
                {
                    "a": c["a"], "b": c["b"],
                    "a_title": id_to_title[c["a"]], "b_title": id_to_title[c["b"]],
                    "distance": c["distance"], "z_score": c["z_score"],
                    "percentile_rank": c["percentile_rank"],
                    "reachable_via_declared_chain": c["reachable_via_declared_chain"],
                }
                for c in missing_links
            ],
        },
    }

    with open("outputs/dashboard_data.json", "w") as f:
        json.dump(export, f, indent=2)
    print("Exported outputs/dashboard_data.json")
    print(f"  nodes={len(nodes_export)}  declared_edges={len(declared_edges_export)}  "
          f"missing_links={len(export['phase2']['missing_links'])}")


if __name__ == "__main__":
    main()
