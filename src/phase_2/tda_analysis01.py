"""
tda_analysis.py
----------------
Why semantic distance, not just graph distance?
The 41-node cross-reference subgraph is a pure forest with ZERO cycles
(verified empirically - see graph_builder.graph_summary). That means beta_1
computed directly from declared "suggested_chain" edges is trivially 0 -
there is no hidden loop structure to discover from the graph alone, because
a forest cannot contain loops by definition.

The actual opportunity for TDA here is to build a CONTINUOUS metric space
from the entries' textual content (title + knowledge + abstracted pattern +
pitfalls) via TF-IDF / cosine distance, then run persistent homology on
THAT space. This lets us discover:
  - semantic clusters that exist independent of the (sparse, manually
    curated) cross-reference graph
  - beta_1 loops: groups of >=3 entries that are all pairwise similar
    without one single best path between them (conceptual redundancy /
    multiple equally-valid framings of a related idea)
  - "missing link" candidates: pairs of entries that are semantically very
    close (would merge early in the filtration) but have NO declared
    cross-reference edge - these are gaps the curators may have missed
"""

import numpy as np
import gudhi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances


def build_text_corpus(ek_entries):
    """One text blob per entry: title + core knowledge + abstracted pattern
    narrative + pitfalls. Order matches the order of ek_entries."""
    corpus = []
    for e in ek_entries:
        parts = [
            e.get("title", ""),
            e.get("knowledge", ""),
            e.get("abstracted_pattern", {}).get("narrative", ""),
            " ".join(e.get("pitfalls", [])),
            " ".join(e.get("abstracted_pattern", {}).get("generalizes_to", [])),
        ]
        corpus.append(" ".join(parts))
    return corpus


def semantic_distance_matrix(corpus, ngram_range=(1, 2), max_features=3000, sublinear_tf=True):
    """TF-IDF + cosine distance. Returns (matrix, vectorizer, tfidf_matrix).
    Uses unigrams+bigrams and sublinear term-frequency scaling, which
    noticeably sharpens separation for short technical text like these
    knowledge entries (bigrams catch phrases like 'encoding inconsistency'
    or 'regex bypass' that unigrams alone dilute)."""
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=max_features,
        ngram_range=ngram_range,
        sublinear_tf=sublinear_tf,
    )
    tfidf = vectorizer.fit_transform(corpus)
    dist = cosine_distances(tfidf)
    np.fill_diagonal(dist, 0.0)
    return dist, vectorizer, tfidf


def compute_persistence(distance_matrix, max_edge_length=1.0, max_dimension=2):
    """Builds a Rips complex on the distance matrix and computes persistent
    homology. Returns (simplex_tree, persistence_list)."""
    rips = gudhi.RipsComplex(
        distance_matrix=distance_matrix, max_edge_length=max_edge_length
    )
    simplex_tree = rips.create_simplex_tree(max_dimension=max_dimension)
    persistence = simplex_tree.persistence()
    return simplex_tree, persistence


def betti_curve(simplex_tree, max_dim=1, n_steps=60, max_eps=1.0):
    """Sweeps epsilon from 0 to max_eps and records Betti numbers at each
    step, by re-querying the (already computed) persistence pairs.
    Returns dict: {dim: [(eps, betti_dim), ...]}."""
    eps_values = np.linspace(0.0, max_eps, n_steps)
    betti_over_time = {d: [] for d in range(max_dim + 1)}
    for eps in eps_values:
        bettis = simplex_tree.persistent_betti_numbers(eps, eps)
        for d in range(max_dim + 1):
            b = bettis[d] if d < len(bettis) else 0
            betti_over_time[d].append((eps, b))
    return betti_over_time


def long_persisting_features(persistence, dim=1, min_persistence=0.05):
    """Filters persistence pairs for a given homology dimension whose
    (death - birth) exceeds min_persistence - these are the 'real'
    topological features rather than filtration noise."""
    out = []
    for d, (birth, death) in persistence:
        if d != dim:
            continue
        if death == float("inf"):
            out.append((birth, death))
            continue
        if (death - birth) >= min_persistence:
            out.append((birth, death))
    return sorted(out, key=lambda bd: (bd[1] - bd[0]) if bd[1] != float("inf") else float("inf"), reverse=True)


def find_missing_link_candidates(distance_matrix, node_ids, existing_edges, top_k=10, max_distance=0.55):
    """Pairs of nodes that are semantically very close (small distance) but
    have NO declared cross-reference edge in either direction. These are
    candidate 'gaps' in the curated knowledge graph.

    Each candidate also gets a z-score and percentile rank against the FULL
    distribution of all pairwise distances, so the claim "these are
    unusually close" is a statistical statement, not just a fixed cutoff.
    """
    existing_pairs = set()
    for a, b in existing_edges:
        existing_pairs.add(frozenset((a, b)))

    n = len(node_ids)
    all_dists = distance_matrix[np.triu_indices(n, k=1)]
    mean_d, std_d = all_dists.mean(), all_dists.std()

    candidates = []
    for i in range(n):
        for j in range(i + 1, n):
            pair_key = frozenset((node_ids[i], node_ids[j]))
            if pair_key in existing_pairs:
                continue
            d = distance_matrix[i, j]
            if d <= max_distance:
                z = (d - mean_d) / std_d if std_d > 0 else 0.0
                percentile = float((all_dists < d).mean() * 100)
                candidates.append((node_ids[i], node_ids[j], d, z, percentile))
    candidates.sort(key=lambda x: x[2])
    return candidates[:top_k]


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from data_loader import load_experiential_knowledge, load_cross_references

    ek = load_experiential_knowledge("data/experiential_knowledge_41.json")
    edges, _ = load_cross_references("data/cross_references.json")
    node_ids = [e["id"] for e in ek]

    corpus = build_text_corpus(ek)
    dist, vec, tfidf = semantic_distance_matrix(corpus)
    print("Distance matrix shape:", dist.shape)
    print("Mean pairwise distance:", dist[np.triu_indices_from(dist, k=1)].mean().round(3))

    simplex_tree, persistence = compute_persistence(dist, max_edge_length=1.0, max_dimension=2)
    loops = long_persisting_features(persistence, dim=1, min_persistence=0.03)
    print(f"Long-persisting beta_1 loops found: {len(loops)}")

    sample_edges = [(a, b) for a, b in edges if a in node_ids and b in node_ids]
    candidates = find_missing_link_candidates(dist, node_ids, sample_edges, top_k=5)
    print("Top missing-link candidates (semantically close, no declared edge):")
    for a, b, d, z, pct in candidates:
        print(f"  {a} <-> {b}  distance={d:.3f}  z={z:.2f}  closer_than={pct:.1f}% of all pairs")
