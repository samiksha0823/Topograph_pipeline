import os
import sys
from collections import Counter

import networkx as nx
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from flask import Flask, render_template_string


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(BASE_DIR, "src")


if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)



from src.final_phase.data_loader import (
    load_experiential_knowledge,
    load_quality_metrics,
    load_cross_references
)

from src.final_phase.graph_builder import (
    build_knowledge_graph,
    graph_summary
)

from src.final_phase.graph_analytics import (
    centrality_report,
    fragmentation_report
)

from src.final_phase.tda_analysis import (
    build_text_corpus,
    semantic_distance_matrix,
    compute_persistence,
    betti_curve
)

app = Flask(__name__, 
            template_folder=TEMPLATE_FOLDER, 
            static_folder="static")


CATEGORY_COLORS = {
    "Domain Knowledge": "#6366F1",         
    "Technical Specification": "#E07A5F", 
    "Process Model": "#10B981",           
    "Validation Rule": "#F59E0B"           
}



def create_network_graph(G):
    pos = nx.spring_layout(G, seed=42, k=1)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        hoverinfo="skip",
        line=dict(width=1, color="#4B5563")
    )

    node_x = []
    node_y = []
    node_color = []  
    node_size = []   
    node_text = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
       
        deg = G.degree(node)
        node_color.append(deg)          
        node_size.append(20 + deg * 4)  
        
        cat = G.nodes[node].get("category", "Domain Knowledge")
        node_text.append(
            f"<b>Node ID:</b> {node}<br>"
            f"<b>Title:</b> {G.nodes[node].get('title', 'N/A')}<br>"
            f"<b>Category:</b> {cat}<br>"
            f"<b>Connections:</b> {deg}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        text=node_text,
        hovertemplate="%{text}<extra></extra>",
        marker=dict(
            size=node_size,
            color=node_color,
            
            colorscale=[
                [0.0, "#8FF084"],  
                [0.5, "#ED3737"],  
                [1.0, "#f9e746"]  
            ],
            showscale=True,        
            line=dict(width=1.5, color="white")
        )
    )

    fig = go.Figure([edge_trace, node_trace])

    fig.update_layout(
        title="01. Knowledge Graph Network Topology",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        height=650,
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')



def create_healed_network_graph(G, missing_link_candidates):
    pos = nx.spring_layout(G, seed=42, k=1)

    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        hoverinfo="skip",
        line=dict(width=1, color="#4B5563")
    )

   
    heal_x = []
    heal_y = []
    for c in missing_link_candidates:
        
        if isinstance(c, dict):
            a, b = c.get("a"), c.get("b")
        else:
            a, b = c[0], c[1]
            
        if a in pos and b in pos:
            heal_x += [pos[a][0], pos[b][0], None]
            heal_y += [pos[a][1], pos[b][1], None]

    heal_trace = go.Scatter(
        x=heal_x, y=heal_y,
        mode="lines",
        name="Healed Path",
        hoverinfo="skip",
        line=dict(color="#EF4444", width=2.5, dash="dash") # Signature Red Dashed Line
    )

    
    node_x = []
    node_y = []
    node_color = []
    node_size = []
    node_text = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        deg = G.degree(node)
        node_color.append(deg)
        node_size.append(20 + deg * 4)
        
        cat = G.nodes[node].get("category", "Domain Knowledge")
        node_text.append(
            f"<b>Node ID:</b> {node}<br>"
            f"<b>Category:</b> {cat}<br>"
            f"<b>Connections:</b> {deg}"
        )

   
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        text=node_text,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,  
        marker=dict(
            size=node_size,
            color=node_color,
            colorscale=[
                [0.0, "#8FF084"], 
                [0.5, "#ED3737"], 
                [1.0, "#f9e746"]  
            ],
            showscale=False,     
            line=dict(width=1.5, color="white")
        )
    )

    fig = go.Figure([edge_trace, heal_trace, node_trace])

    fig.update_layout(
        title="01b. Post-TDA Automated Network Structural Healing Map (Missing Links in Red)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        height=650,
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=True,
        legend=dict(font=dict(color='#9CA3AF'), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)

def create_centrality_graph(rows=None):
    try:
        top_rows = rows[:10] if rows and len(rows) > 10 else (rows if rows else [])
        
        # Pulls IDs and checks for matching label context metadata safely
        nodes = [f"{r.get('id', 'Unknown')}<br>{r.get('label', '')}" for r in top_rows] if top_rows else ["No Data"]
        out_degrees = [r.get("out_degree", 0) for r in top_rows] if top_rows else [0]
        in_degrees = [r.get("in_degree", 0) for r in top_rows] if top_rows else [0]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=nodes, x=out_degrees, name="Out Degree", orientation='h', marker_color='#E07A5F',
            hovertemplate="<b>Node:</b> %{y}<br><b>Out Degree:</b> %{x}<extra></extra>"
        ))
        fig.add_trace(go.Bar(
            y=nodes, x=in_degrees, name="In Degree", orientation='h', marker_color='#3B426E',
            hovertemplate="<b>Node:</b> %{y}<br><b>In Degree:</b> %{x}<extra></extra>"
        ))

        fig.update_layout(
            title="02. Top Entries by Declared-Chain Connectivity",
            barmode="group",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0', size=10),
            height=450,
            margin=dict(l=180, r=20, t=50, b=40),
            yaxis=dict(autorange="reversed", tickmode="array", automargin=True),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig.to_html(full_html=False, include_plotlyjs=False)
    except Exception as e:
        print(f"Centrality Graph Error: {e}")
        return "<div class='card'>Centrality chart generation error</div>"


def create_category_graph(ek):
    counts = Counter(e["category"] for e in ek)
    cats = list(counts.keys())
    vals = [counts[c] for c in cats]
    colors = [CATEGORY_COLORS.get(c, "#9CA3AF") for c in cats]

    fig = go.Figure(data=[go.Bar(
        x=cats, y=vals, marker_color=colors,
        hovertemplate="<b>Category:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>"
    )])

    fig.update_layout(
        title="03. Knowledge Category Distribution",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        height=420,
        margin=dict(l=40, r=20, t=50, b=40)
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)



def create_persistence_graph(persistence):
    fig = go.Figure()
    dim_colors = {0: "#6366F1", 1: "#E07A5F", 2: "#10B981"}

    for dim in [0, 1, 2]:
        births = []
        deaths = []
        for d, (b, death) in persistence:
            if d == dim:
                births.append(b)
                deaths.append(1.0 if death == float("inf") else death)

        fig.add_trace(go.Scatter(
            x=births, y=deaths, mode="markers", name=f"H{dim}",
            marker=dict(size=10, color=dim_colors.get(dim, "gray"), line=dict(width=1, color="white")),
            hovertemplate=f"<b>Dimension:</b> H{dim}<br><b>Birth:</b> %{{x:.4f}}<br><b>Death:</b> %{{y:.4f}}<extra></extra>"
        ))

    fig.add_shape(type="line", line=dict(dash="dash", color="#4B5563", width=1), x0=0, y0=0, x1=1, y1=1)
    fig.update_layout(
        title="04. Topological Persistence Diagram",
        xaxis_title="Birth", yaxis_title="Death",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'), height=420, margin=dict(l=50, r=20, t=50, b=50)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)




def create_barcode_graph(persistence, max_dim=1, max_bars_per_dim=25):
    dim_colors = {0: "#6366F1", 1: "#E07A5F", 2: "#10B981"}
    finite_max = max((death for _, (b, death) in persistence if death != float("inf")), default=1.0)
    plot_max = finite_max * 1.05

    rows = []
    for d in range(max_dim + 1):
        feats = sorted(
            [(b, death) for dd, (b, death) in persistence if dd == d],
            key=lambda bd: (bd[1] - bd[0]) if bd[1] != float("inf") else float("inf"),
            reverse=True
        )[:max_bars_per_dim]
        for b, death in feats:
            rows.append((d, b, death if death != float("inf") else plot_max, death == float("inf")))

    fig = go.Figure()
    for i, (d, b, death, is_infinite) in enumerate(rows):
        fig.add_trace(go.Scatter(
            x=[b, death], y=[i, i], mode="lines+markers" if is_infinite else "lines",
            line=dict(color=dim_colors.get(d, "gray"), width=4),
            showlegend=False,
            hovertemplate=f"<b>Dimension:</b> H{d}<br><b>Birth:</b> %{{x[0]:.4f}}<br><b>Death:</b> {('∞' if is_infinite else '%{x[1]:.4f}')}<extra></extra>"
        ))

    fig.update_layout(
        title="05. Topological Persistence Barcode",
        xaxis_title="Filtration Scale (Semantic Distance)",
        yaxis=dict(showticklabels=False, showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'), height=420, margin=dict(l=40, r=20, t=50, b=40)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)




def create_betti_graph(betti):
    fig = go.Figure()

    for dim, series in betti.items():
        fig.add_trace(go.Scatter(
            x=[x for x, _ in series],
            y=[y for _, y in series],
            mode="lines",
            name=f"β{dim} Loops" if dim == 1 else f"β{dim} Components",
            line=dict(width=3),
            hovertemplate="Threshold: %{x:.2f}<br>Count: %{y}<extra></extra>"
        ))

    fig.update_layout(
        title="06. Betti Continuity Diagnosis Curve",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        height=420,
        hovermode="x unified",
        xaxis_title="Filtration Scale",
        yaxis_title="Betti Number Count"
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)




def create_summary_pie(summary):
    fig = px.pie(
        values=[summary["n_edges"], summary["n_isolated_nodes"]],
        names=["Connected Nodes", "Isolated Nodes"],
        title="06. Node Fragment Distribution Summary",
        color_discrete_sequence=['#10B981', '#EF4444'],
        hole=0.4
    )

    fig.update_traces(
        hovertemplate="<b>Status:</b> %{label}<br><b>Count:</b> %{value}<br><b>Percentage:</b> %{percent}<extra></extra>"
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        height=420,
        margin=dict(l=20, r=20, t=50, b=40)
    )

    config_options = {
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['toggleHover', 'textMode'],
        'displaylogo': False
    }

    return fig.to_html(full_html=False, include_plotlyjs=False, config=config_options)




@app.route("/")
def index():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Change this line in your index() function
    template_path = r"C:\Users\Harini Madasu\ieee_data\Topograph_pipeline\src\final_phase\templates.py\index.html"
    
    PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")

    # 2. Read the file content
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    ek = load_experiential_knowledge(os.path.join(DATA_DIR, "experiential_knowledge_41.json"))
    _, quality, _ = load_quality_metrics(os.path.join(DATA_DIR, "quality_metrics.json"))
    edges, _ = load_cross_references(os.path.join(DATA_DIR, "cross_references.json"))

    
    G = build_knowledge_graph(ek, quality, edges)

    summary = graph_summary(G)
    central = centrality_report(G)

    corpus = build_text_corpus(ek)
    dist, _, _ = semantic_distance_matrix(corpus)

    simplex_tree, persistence = compute_persistence(dist)
    betti = betti_curve(simplex_tree)

   
    node_ids = list(G.nodes())
    actual_missing_links = []
    
    
    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            node_a = node_ids[i]
            node_b = node_ids[j]
            
            
            if dist[i, j] < 0.5 and not G.has_edge(node_a, node_b):
                actual_missing_links.append((node_a, node_b))
    

    cards_payload = [
        {"label": "Total Loaded Nodes", "value": summary.get("n_nodes", len(G.nodes()))},
        {"label": "Isolated Fragments", "value": summary.get("n_isolated_nodes", 0)},
        {"label": "Structural Relationships", "value": summary.get("n_edges", len(G.edges()))}
    ]

    return render_template_string(
        html_content,
        cards=cards_payload,
        network=create_network_graph(G),
        
        healed_network=create_healed_network_graph(G, actual_missing_links), 
        centrality=create_centrality_graph(central),
        category=create_category_graph(ek),
        persistence=create_persistence_graph(persistence),
        barcode=create_barcode_graph(persistence),
        betti=create_betti_graph(betti),
        summarypie=create_summary_pie(summary)
    )

if __name__ == "__main__":
   
    app.run(port=5000)