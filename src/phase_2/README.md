# TopoGraph: The Ontology Healer

A two-phase TDA pipeline for the **Knowledge Graph Analytics and Discovery**
hackathon track, built on the three provided dataset files
(`experiential_knowledge_41.json`, `quality_metrics.json`, `cross_references.json`).

## The pitch in one line
Standard graph analytics are structurally blind to human curation errors.
We use Topological Data Analysis to (1) *prove* the curated attack-chain
graph has zero recursive loops at any quality threshold, and (2) *heal* it
by discovering statistically defensible missing links a human curator
never connected.

## Pipeline architecture (matches the team's two-phase plan)

### Phase 1 - Diagnose (`quality_filtered_tda.py`)
Builds a Vietoris-Rips complex whose 1-skeleton is restricted to ONLY the
declared cross-reference edges, with distance derived from each pair's
quality score (`1 - min(quality_a, quality_b)/8`). Non-edges get a sentinel
distance so they can never enter the complex.

**Central result — a proof, not just an observation:** the declared graph
satisfies `n_edges = n_nodes - n_components` (14 = 41 - 27), the exact
identity that holds iff a graph is a forest. Any subgraph of a forest is
itself a forest, so **β₁ = 0 at every quality threshold by construction**.
`prove_zero_beta1(G)` checks this formally; the persistence computation
then empirically confirms it (0 H₁ features found).

Honest caveat: the 8-point binary quality checklist is nearly saturated
(38/41 entries score a perfect 8/8), so the *fragmentation* effect of
stricter validation is real but modest (29 → 27 components) — reported
as-is rather than oversold.

### Phase 2 - Heal (`tda_analysis.py` + `missing_link_healer.py`)
Builds a second, continuous metric space from entry text (TF-IDF + cosine
distance) — independent of the (acyclic) declared-edge graph — and runs
persistent homology on it. `missing_link_healer.py` then walks the Rips
filtration's own merge order (the literal order entries would topologically
connect) and flags pairs that are statistically very close but were never
cross-referenced, reporting:
- z-score and percentile rank vs. the full pairwise-distance distribution
- whether the pair is reachable via ANY chain of declared edges at all

All 5 top candidates found are NOT reachable via any declared chain at all
(z ≈ -6 to -8.5, i.e. 6-8.5 standard deviations closer than average) — the
strongest possible evidence of a curation gap.

## Run it

```bash
pip install networkx gudhi matplotlib numpy scipy scikit-learn
python3 main.py
```

(Also runs fine in Google Colab — same `pip install` line works there.)

## Outputs (`outputs/`)
| File |  Description |
|---|---|---|
| `01_network_graph.png` | Declared cross-reference graph, by category |
| `02_centrality.png` | Top entries by in/out-degree |
| `03_category_distribution.png` | Category counts |
| `06_phase1_quality_fragmentation.png` | β₀/β₁ vs. quality threshold — proves β₁=0 |
| `04_persistence_diagram.png` |  H₀/H₁ scatter diagram, semantic space |
| `07_persistence_barcode.png` | Classic barcode view of the same |
| `08_before_after_healing.png` |"Before/After" — missing links drawn in red |
| `findings_summary.md` | Full write-up, paste straight into the script/slides |

## File structure
```
data_loader.py          # robust JSON loading (handles trailing-comma bug)
graph_builder.py         # builds the networkx DiGraph + structural summary
graph_analytics.py       # centrality, longest chains, category bridges
quality_filtered_tda.py  # PHASE 1: proof + quality-filtered persistence
tda_analysis.py          # PHASE 2: TF-IDF semantic distance + persistence
missing_link_healer.py   # PHASE 2: filtration-order-based missing-link detection + stats
visualize.py             # all matplotlib figures, including barcode + before/after
main.py                  # orchestrates both phases, writes findings_summary.md
data/                    # the 3 provided JSON files
outputs/                 # generated figures + findings_summary.md
```


