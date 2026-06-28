# TopoGraph

**Topological Data Analysis for Structural Auditing and Semantic Healing of Security Knowledge Graphs**

> Team InsightX — IEEE DataPort Hackathon | Knowledge Graph Analytics and Discovery Track
> Team: Samiksha, M Tarunima Rao, Harini, Reza

---

## Overview

Security knowledge graphs curated by humans are structurally fragile: conventional graph analytics (Cypher/SPARQL queries, centrality algorithms) capture only local, pairwise structure and miss macro-level vulnerabilities. TopoGraph addresses this with a **dual-pipeline TDA-driven system** that applies persistent homology to a 41-node Security Experiential Knowledge Graph, surfacing structural flaws and semantic gaps that are invisible to all pairwise graph metrics.

### What TopoGraph Detects

| Problem | TDA Signal | Conventional Tool |
|---|---|---|
| Fragile single-point-of-failure nodes | β₀ persistence | ❌ Missed |
| Circular exploit chains / reasoning loops | β₁ loops | ❌ Missed |
| Information bottlenecks | Persistent topological features | ❌ Missed |
| Missing semantic links between equivalent techniques | Semantic TDA | ❌ Missed |

---

## Key Results

- **Zero circular dependencies** — TopoGraph mathematically proved the human-curated ontology contains no recursive exploit loops (β₁ = 0 across all filtration scales).
- **High fragility under strict quality filtering** — The Betti-0 curve reveals that filtering strictly by perfect quality metrics causes the intelligence graph to completely fragment.
- **5 critical missing links discovered** — The semantic pipeline automatically identified uncurated connections (e.g., `ek_0032 ↔ ek_0033`), enabling self-healing of the ontology without human re-curation.

---

## Architecture

TopoGraph runs two independent pipelines that together produce a complete structural + semantic audit:

```
Pipeline 1 — Structural TDA          Pipeline 2 — Semantic TDA
────────────────────────────          ──────────────────────────
Graph → 8D quality metric vector  →   Embed node text via TF-IDF
     → Vietoris-Rips complex      →   Build semantic distance space
     → Persistence diagrams       →   Cross-reference topological events
     → β₀, β₁ Betti numbers       →   Against human-curated edges
     → Flag bottlenecks & chains  →   Surface missing semantic links
```

---

## Dataset

**IEEE DataPort Hackathon dataset (CC BY 4.0)** — 41 Security Experiential Knowledge entries.

| File | Contents |
|---|---|
| `experiential_knowledge_41.json` | 41 entries (`ek_0000`–`ek_0040`): title, category, core knowledge, trigger condition, IF…THEN pattern, pitfalls, chain potential, confidence, shelf-life |
| `quality_metrics.json` | 8-dimensional binary quality checklist per entry (avg. derivability: 0.443, condition richness: 0.771, abstraction quality: 0.284) |
| `cross_references.json` | Directed `suggested_chain` edges — full topology spans 85 edges; 14 fall inside the 41-node sample |

**Category breakdown:** chain\_pattern (13) · signal\_interpretation (12) · tactical\_priority (8) · bypass\_technique (7) · pitfall (1)

---

## Technology Stack

| Library | Role |
|---|---|
| **NetworkX** | Builds and queries the 41-node directed knowledge graph; traversal, centrality, subgraph analysis |
| **GUDHI** | Constructs simplicial complexes, computes persistent homology, extracts Betti numbers across filtration scales |
| **Matplotlib** | Renders persistence diagrams, barcode plots, and topology heatmaps |
| **scikit-learn** | TF-IDF vectorization for the semantic pipeline |
| **NumPy / SciPy** | Numerical computation and distance matrix construction |

---

## Project Structure

```
├── data/
│   ├── experiential_knowledge_41.json   # IEEE DataPort knowledge entries
│   ├── quality_metrics.json             # 8D quality checklist per entry
│   └── cross_references.json            # Directed suggested_chain edges
├── outputs/
│   ├── 04a_quality_betti_curves.png     # β₀ fragmentation + β₁ loop proof
│   ├── 04b_semantic_persistence.png     # Persistence barcode (semantic space)
│   └── findings_summary_unified.md      # Decision-ready intelligence report
├── src/
│   ├── data_loader.py                   # Robust JSON parsing (handles malformed trailing commas)
│   ├── graph_builder.py                 # NetworkX DiGraph initialization
│   ├── graph_analytics.py              # Centrality and fragmentation metrics
│   ├── tda_analysis.py                 # Core GUDHI SimplexTree + NLP logic
│   ├── visualize.py                    # Matplotlib chart generation
│   └── main.py                         # Pipeline orchestrator
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/topograph.git
cd topograph
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install networkx gudhi matplotlib numpy scipy scikit-learn
```

---

## Running the Pipeline

Execute the main orchestrator from the project root:

```bash
python src/main.py
```

The pipeline completes both phases in seconds. All outputs are written to the `outputs/` directory.

---

## Outputs

| File | Description |
|---|---|
| `04a_quality_betti_curves.png` | Mathematical proof of graph fragmentation (β₀) and absence of recursive loops (β₁ = 0) |
| `04b_semantic_persistence.png` | Persistence barcode of the semantic TF-IDF vector space |
| `findings_summary_unified.md` | Complete decision-ready intelligence report — includes exact node IDs and semantic distances of all discovered missing links |

---

## Methodology

### Pipeline 1 — Structural TDA

1. Build an 8-dimensional quality metric feature vector per graph node
2. Construct a filtered Vietoris-Rips simplicial complex over those vectors
3. Compute persistence diagrams across filtration scales
4. Extract topologically significant features above the noise threshold
5. Map features back to the graph — flag bottlenecks, exploit chains, and isolated components

**β₀ (Betti-0)** counts connected components — reveals fragmentation and single-point dependencies.
**β₁ (Betti-1)** counts independent cycles — reveals circular reasoning chains and recursive exploit loops.

### Pipeline 2 — Semantic TDA

1. Embed node text (title + core knowledge) into a continuous TF-IDF vector space
2. Compute pairwise semantic distance matrix
3. Build a filtered simplicial complex over the semantic space
4. Cross-reference topological proximity events against human-curated edges
5. Surface node pairs that are semantically close but disconnected in the curated graph

---

## Impact & Recommendations

TopoGraph generates four categories of actionable output:

1. **Sever or duplicate fragile dependency nodes** — reduce β₀ fragility from single-point-of-failure structures.
2. **Refactor circular attack-technique chains** — ground β₁ loops in external evidence anchors.
3. **Add redundant edges around persistent bottlenecks** — eliminate choke points where disproportionate knowledge flows concentrate.
4. **Insert semantically-inferred edges** — heal missing curator connections automatically discovered by the semantic pipeline.

---

## Real-World Applications

TopoGraph's TDA-healing approach generalizes beyond the hackathon dataset:

- **Pentest / Red-Team Knowledge Bases** — nightly QA jobs flagging technique pairs that should be cross-referenced before the knowledge base becomes too large to audit manually.
- **Threat-Intel (CTI) Graph QA** — MITRE ATT&CK-style and vendor CTI graphs face the same fragmentation/missing-link problem at thousands-of-node scale.
- **Bug Bounty / Disclosure Mining** — continuously ingest HackerOne/Bugcrowd write-ups into a structured, self-healing internal knowledge graph.
- **Security Training & Onboarding** — visualize the topology of what a team knows; isolated technique islands reveal blind spots a flat list would never surface.

The same approach applies to any large curated knowledge graph — medical guidelines, legal case-law citations, scientific literature.

---

## Future Work — LLM Augmented Pipeline

A planned 6-stage extension adds an LLM layer at both ends of the pipeline (CPU-only, zero fine-tuning — inference on an off-the-shelf instruction model):

```
Security Docs → LLM Extracts Entities & Relations → Security KG
→ TopoGraph (TDA) → Detect Structural Problems → LLM Explains & Suggests Repairs
```

- **Stage 1 (Entity Extraction):** A pretrained instruction LLM (Qwen2.5-3B-Instruct via Ollama, fully local CPU inference) extracts new entries from raw pentest write-ups, matching the exact dataset schema. Every extracted entry is schema-validated before acceptance.
- **Stage 6 (Explanation & Repair Drafting):** The same model translates TopoGraph's mathematical findings into plain language and drafts ready-to-review cross-reference edges for each missing link — tagged `requires_human_approval`, never auto-merged.

Why pretrained, not fine-tuned: no GPU needed, and a pluggable backend (local Ollama or any OpenAI-compatible API) means the rest of the pipeline never changes when the model does.

---

