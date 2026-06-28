# TopoGraph: Topological Knowledge Graph Analytics & Healing

A comprehensive data pipeline for the **Knowledge Graph Analytics and Discovery** hackathon track. It ingests three core dataset files (`experiential_knowledge_41.json`, `quality_metrics.json`, and `cross_references.json`) to diagnose structural gaps and heal fragmented relationships using **Topological Data Analysis (TDA)**.

> **Team:** M. Tarunima Rao · Samiksha · Harini · Reza

---

## Table of Contents

- [What It Does](#what-it-does)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Pipeline](#running-the-pipeline)
- [Outputs](#outputs)
- [Key Findings & Impact](#key-findings--impact)

---

## What It Does

1. **Robust Data Loading** — Automatically ingests datasets and sanitizes structural inconsistencies (such as trailing commas in `experiential_knowledge_41.json`) natively.
2. **Directed Network Analytics** — Constructs a directed knowledge graph from raw cross-reference chains to assess degree centrality, longest sequential chains, and cross-category bridging transitions.
3. **Quality-Filtered Topology (The Diagnosis)** — Evaluates how stringent quality validation metrics affect network coherence. Isolates subgraphs based on an 8-dimensional checklist to visualize fragmentation.
4. **Semantic TDA & Automated Healing (The Cure)** — Maps textual entry content into a continuous metric space using TF-IDF vectorization and a cosine distance matrix. Persistent homology via `gudhi` across the filtration surfaces "missing link" candidates — highly similar items separated by human curators.
5. **Reporting & Visualization** — Generates complete analytical plots alongside a formatted summary document.

---

## Project Structure

```text
TopoGraph/
├── data/                               # IEEE DataPort JSON datasets
├── outputs/                            # Generated charts and findings report
├── src/
│   ├── data_loader.py                  # Robust JSON parsing
│   ├── graph_builder.py                # NetworkX DiGraph initialization
│   ├── graph_analytics.py              # Centrality and fragmentation metrics
│   ├── tda_analysis.py                 # Core GUDHI SimplexTree and NLP logic
│   ├── visualize.py                    # Matplotlib generation
│   └── main.py                         # Pipeline orchestrator
└── README.md
```

---

## Setup & Installation

**1. Set up a Virtual Environment (Recommended)**

```bash
python3 -m venv .venv
source .venv/bin/activate       # On Windows use: .venv\Scripts\activate
```

**2. Install Dependencies**

```bash
pip install networkx gudhi matplotlib numpy scipy scikit-learn
```

---

## Running the Pipeline

Execute the main orchestrator script from the root directory:

```bash
python src/main.py
```

The pipeline executes both phases in seconds.

---

## Outputs

All results are generated in the `outputs/` directory:

| File | Description |
|------|-------------|
| `04a_quality_betti_curves.png` | Mathematical proof of graph fragmentation (β₀) and zero recursive loops (β₁) |
| `04b_semantic_persistence.png` | Persistence barcode of the semantic vector space |
| `findings_summary_unified.md` | Complete, decision-ready intelligence report including exact node IDs and semantic distances of all discovered missing links |

---

## Key Findings & Impact

**Zero Circular Dependencies**
TopoGraph mathematically proved that the human-curated ontology contains no recursive exploit loops (β₁ = 0).

**High Quality-Dependency Fragility**
The Betti-0 curve reveals that filtering the graph strictly by perfect quality metrics causes the intelligence vectors to completely shatter into isolated components, obscuring multi-hop attack vectors.

**Automated Graph Healing**
The engine successfully identified **5 critical missing links** (e.g., `ek_0032 ↔ ek_0033`). TopoGraph acts as a self-healing ontology framework, dramatically reducing human error in threat intelligence databases.

---

*Built for the Knowledge Graph Analytics and Discovery Hackathon track.*
