# TopoGraph: The Ontology Healer - Findings Summary

## 0. Dataset structure

- 41 knowledge entries loaded (ek_0000-ek_0040).
- Quality checklist (8 binary dimensions) is nearly saturated: avg_pass_count=0.469; 38 of 41 entries score a perfect 8/8, only 3 score 7/8. So quality variance is real but small.
- Cross-reference file contains 85 total directed edges (full topology up to ek_0253), but only **14** fall inside our 41-node sample.

## 1. PHASE 1 - Diagnose: Quality-Filtered TDA

**Formal proof, not just an observation:** The declared cross-reference graph satisfies n_edges = n_nodes - n_components (14 = 41 - 27), the exact identity that holds iff a graph is a forest. Any quality-filtered subgraph of this edge set is therefore also a forest, and any flag/Rips complex whose 1-skeleton is restricted to these edges has beta_1 = 0 at every filtration threshold - not by observation, but by construction.

- Verified: n_edges (14) = n_nodes (41) - n_components (27) -> exact forest identity holds: True.
- Empirical confirmation: running the quality-filtered Rips complex across the full epsilon range found **zero H1 features**, matching the proof exactly.
- Fragmentation effect of strict validation is real but modest with this dataset: 29 components when only perfect-quality (8/8) edges are trusted, vs 27 when all declared edges are trusted regardless of quality (only 2 of 14 edges touch a 7/8-quality node, so the swing is small). We report this honestly rather than oversell a dramatic 'shattering' effect.

### Category transitions in the declared chains
- signal_interpretation -> chain_pattern: 3
- tactical_priority -> chain_pattern: 2
- chain_pattern -> bypass_technique: 2
- signal_interpretation -> bypass_technique: 1
- tactical_priority -> pitfall: 1
- bypass_technique -> pitfall: 1
- bypass_technique -> signal_interpretation: 1
- chain_pattern -> chain_pattern: 1
- tactical_priority -> signal_interpretation: 1
- bypass_technique -> chain_pattern: 1

### Longest declared chains
- ek_0002 (Tiered URL decode rejection flags leave ) -> ek_0003 (location.pathname double-slash protocol-)
- ek_0012 (Prioritize compound-state pages when tes) -> ek_0014 (Plaintext tag destroys page rendering ma)
- ek_0013 (HTML blacklist bypass via deprecated and) -> ek_0014 (Plaintext tag destroys page rendering ma)
- ek_0016 (Encoder/decoder asymmetry as vulnerabili) -> ek_0017 (Multiplier overflow to zero silently con)
- ek_0018 (Audit protocol spec mandatory limits as ) -> ek_0019 (Server-side data fetch + content-type mi)

## 2. PHASE 2 - Heal: Semantic TDA & Missing Link Discovery

Since beta_1 cannot exist in a graph built only from declared (forest) edges, healing requires a continuous metric space independent of those edges. We built one from entry text (TF-IDF + cosine distance) and used the Rips filtration's own merge order - the literal order in which entries would topologically connect - to find missing links, rather than an arbitrary distance cutoff. Background: mean pairwise distance = 0.9543, std = 0.0425, n_pairs = 820.

### Top 5 healed missing links (statistically defensible)
- **ek_0032 <-> ek_0033** (distance=0.5922, z=-8.52, percentile=0.0%, NOT reachable via any declared chain)
    "Fragment-routed AJAX + unanchored regex domain check = " <-> "Satisfying unanchored domain regex via query parameter "
- **ek_0000 <-> ek_0001** (distance=0.656, z=-7.02, percentile=0.24%, NOT reachable via any declared chain)
    "curl Proxy-Authorization leak on proxy-to-direct redire" <-> "Proxy-to-direct redirect as credential harvesting vecto"
- **ek_0032 <-> ek_0034** (distance=0.6724, z=-6.63, percentile=0.37%, NOT reachable via any declared chain)
    "Fragment-routed AJAX + unanchored regex domain check = " <-> "Fragment-based AJAX routing signals potential CORS-assi"
- **ek_0024 <-> ek_0025** (distance=0.6767, z=-6.53, percentile=0.49%, NOT reachable via any declared chain)
    "CRLF injection + missing pingpong overflow check enable" <-> "When auditing pingpong protocol handlers, diff the over"
- **ek_0003 <-> ek_0032** (distance=0.6886, z=-6.25, percentile=0.61%, NOT reachable via any declared chain)
    "location.pathname double-slash protocol-relative URL hi" <-> "Fragment-routed AJAX + unanchored regex domain check = "