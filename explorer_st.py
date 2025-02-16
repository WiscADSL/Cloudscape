# streamlit run explorer_st.py
import streamlit as st
from cloudscape import load_studies as _load_studies
from cloudscape import extract_svc_info as _extract_svc_info
from st_cytoscape import cytoscape
import networkx as nx


@st.cache_data
def load_architectures():
    archs = _load_studies("data/graphs")
    archs.sort(key=lambda x: x.nx_graph.graph["name"])
    return archs


@st.cache_data
def load_svc_info():
    return _extract_svc_info("data/services.csv")


def generate_elements_for_nxgraph(nx_graph: nx.MultiDiGraph):
    flow_colors = [
        "black",
        "red",
        "green",
        "blue",
        "brown",
        "purple",
        "orange",
        "pink",
        "yellow",
        "cyan",
    ] + ["gray"] * 20

    elements = []
    for node_id, node in nx_graph.nodes(data=True):
        svc = node["service"]

        if svc == "ThirdParty":
            label = node["name"]
        else:
            label = svc

        elements.append(
            {
                "data": {
                    "id": node_id,
                    "label": f"{label} ({node_id})",
                    "url": "/app/static/icons/" + svc_info[svc]["image_url"] + ".png",
                    "border_width": 1,
                },
            }
        )

    for u, v, edge_data in nx_graph.edges(data=True):
        elements.append(
            {
                "data": {
                    "source": u,
                    "target": v,
                    "width": 2,
                    "label": edge_data["seq"],
                    "linestyle": "dashed" if edge_data["type"] != "data" else "solid",
                    "color": flow_colors[edge_data["flow_id"]],
                }
            }
        )

    stylesheet = [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "font-size": 9,
                "width": 50,
                "height": 50,
                "background-fit": "cover",
                "background-image": "data(url)",
                "border-width": "data(border_width)",
                "border-color": "black",
                "border-style": "double",
                "text-background-opacity": 1,
                "text-background-color": "#ffffff",
            },
        },
        {
            "selector": "edge",
            "style": {
                "curve-style": "bezier",
                "width": "data(width)",
                "line-style": "data(linestyle)",
                "label": "data(label)",
                "font-size": 8,
                "text-background-opacity": 1,
                "text-background-color": "#ffffff",
                "target-arrow-color": "data(color)",
                "target-arrow-shape": "vee",
                "line-color": "data(color)",
            },
        },
    ]

    return elements, stylesheet


@st.dialog("Interpreting a graph", width="large")
def show_example_architecture():
    graph = nx.MultiDiGraph()
    graph.graph["name"] = "Example Architecture"
    graph.graph["link"] = "https://example.com"
    graph.graph["categories"] = ["Category1", "Category2"]
    graph.graph["graph_usable"] = True
    graph.graph["notes"] = "Some notes about this architecture"

    graph.add_node("1", service="S3", name="")
    graph.add_node("2", service="Lambda", name="")
    graph.add_node("3", service="UserConsumerMobile", name="")
    graph.add_node("4", service="EC2", name="")
    graph.add_node("5", service="EKS", name="")
    graph.add_node("6", service="SageMaker", name="")

    graph.add_edge("3", "4", seq="0", type="control", flow_id=1)
    graph.add_edge("4", "1", seq="1", type="control", flow_id=1)
    graph.add_edge("1", "4", seq="2", type="data", flow_id=1)
    graph.add_edge("4", "3", seq="3", type="data", flow_id=1)

    graph.add_edge("3", "2", seq="0", type="data", flow_id=2)
    graph.add_edge("2", "1", seq="1", type="data", flow_id=2)
    graph.add_edge("2", "5", seq="1'", type="data", flow_id=2)
    graph.add_edge("5", "6", seq="1'.0", type="data", flow_id=2)

    elements, stylesheet = generate_elements_for_nxgraph(graph)
    cytoscape(
        elements, stylesheet, layout={"name": "circle"}, height="400px", width="100%"
    )

    st.write("""
    In this example architecture, there are 2 workflows. Each workflow
    is indicated by edges of different colors. Edges also show a sequence
    number to indicate the order of operations. Bold edges carry data
    while dotted edges are requests or acks.

    In the first (marked red), a request from a mobile app is sent
    to an EC2 instance, which reads from S3 before sending a response
    back to the mobile app.

    In the second workflow (marked green), data from the mobile app
    is sent to a Lambda function. Here, two events happen in
    parallel **(ordering unknown)**. Data is sent to S3, and also to EKS.
    The edge towards S3 is 1, while the edge towards EKS is 1'. EKS
    then sends data to SageMaker, which is denoted as a branched
    seq (1'.0).

    In rare cases where ordering is unknown, seq might be "NA".

    Ref to [README](https://github.com/WiscADSL/Cloudscape) for
    details about different types of nodes.
    """)


st.set_page_config(page_title="Cloudscape: Architecture Explorer")
architectures = load_architectures()
svc_info = load_svc_info()

with st.sidebar:
    st.header("Cloudscape", divider=True)
    st.write(
        "Cloudscape is a dataset that captures how companies stitch different cloud services together to build complex cloud architectures."
    )
    if st.button("Interpreting A Graph", type="secondary", icon=":material/search:"):
        show_example_architecture()
    st.header("Usage Instructions", divider=True)
    st.write(
        """
        This app visualizes the architectures captured in the Cloudscape dataset.
        - Select an architecture from the dropdown to view the architecture or type to search an architecture by name. The architecture explorer is __interactive__.
        - We recommend using light mode for better visibility. You can change the theme from the settings menu from the top right.
        - The wide mode (found in settings) is sometimes helpful for viewing architectures with many nodes.

        ### Common Issues
        - If the architecture diagram is fully zoomed in/out, you can reset it by selecting the architecture again.
        """
    )

st.title("Cloudscape: Architecture Explorer")
st.write(
    "[FAST25 paper](https://www.usenix.org/conference/fast25/presentation/satija) | [Dataset](https://github.com/WiscADSL/Cloudscape) | [BibTeX](https://google.com/)"
)

st.html(
    """
    <style>
    hr {
        border-color: black;
        color: black;
        border: none;
        height: 2px;
        color: black;
        background-color: black;
    }
    </style>

    <hr />
    """
)

arch = st.selectbox(
    "Choose an architecture",
    architectures,
    format_func=lambda x: x.nx_graph.graph["name"],
)

elements, stylesheet = generate_elements_for_nxgraph(arch.nx_graph)
cytoscape(elements, stylesheet, layout={"name": "klay"}, height="600px")  # fcose, klay

graph = arch.nx_graph.graph
st.write(f"**Source**: {graph['link']}")
st.write(f"**Categories**: {graph['categories']}")
if not graph["graph_usable"]:
    st.write(
        "**This architecture was not used in the quantitative analysis of the FAST25 Cloudscape paper.**"
    )

st.write("#### Architecture Notes")
if graph["notes"].strip():
    st.text(graph["notes"].strip())
else:
    st.write("No notes")

st.write("#### Service Notes")
any_notes = False
for node_id, node in arch.nx_graph.nodes(data=True):
    if node["notes"].strip():
        any_notes = True

        if node["service"] == "ThirdParty":
            label = node["name"]
        else:
            label = node["service"]
        name = f"{label} ({node_id})"

        st.write(f"**{name}**: {node['notes'].strip()}")

if not any_notes:
    st.write("No notes")


st.write("#### Edge Notes")
any_notes = False
for src, dst, edge in arch.nx_graph.edges(data=True):
    if edge["notes"].strip():
        any_notes = True
        src = f"{arch.nx_graph.nodes()[src]['service']} ({src})"
        dst = f"{arch.nx_graph.nodes()[dst]['service']} ({dst})"
        st.write(f"**{src} → {dst}**: {edge['notes'].strip()}")

if not any_notes:
    st.write("No notes")
