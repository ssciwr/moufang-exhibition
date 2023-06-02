from dash import Dash, html, Output, Input, State
import dash_cytoscape as cyto
import flask
import json

# Instantiate the Dash app
server = flask.Flask(__name__)
app = Dash(__name__, server=server)

# Load the data file
with open("data.json") as f:
    data = json.load(f)

# Process the data to fit our needs
nodes = []
edges = []

for node in data["nodes"]:
    neighbors = []
    for edge in data["edges"]:
        if node["id"] == edge["source"]:
            neighbors.append(edge["target"])
        if node["id"] == edge["target"]:
            neighbors.append(edge["source"])

    newnode = {
        "data": {
            "id": node["id"],
            "label": node["label"],
            "color": node["color"],
            "size": str(float(node["size"]) * 10),
            "neighbors": neighbors,
        },
        "position": {"x": node["x"], "y": node["y"]},
        "grabbable": False,
    }

    if "kurzinformation" in node["attributes"]:
        newnode["data"]["text"] = node["attributes"]["kurzinformation"]

    if "lebensdaten" in node["attributes"]:
        newnode["data"]["lebensdaten"] = node["attributes"]["lebensdaten"]

    nodes.append(newnode)

for edge in data["edges"]:
    edgedata = {"data": {}}
    edgedata["data"]["source"] = edge["source"]
    edgedata["data"]["target"] = edge["target"]
    # Not reading the original edge id's here allows us to regenerate the graph
    # even without a change to it. This is a horrible hack, but it seems to work.
    # edgedata["data"]["id"] = edge["id"]

    node_colors = []
    for node in data["nodes"]:
        if node["id"] in [edge["source"], edge["target"]]:
            node_colors.append(node["color"])

    assert len(node_colors) == 2
    if node_colors[0] == node_colors[1]:
        edgedata["data"]["color"] = node_colors[0]
    else:
        edgedata["data"]["color"] = "#666666"

    edges.append(edgedata)


# The sidebar CSS
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "hidden",
}

# The sidebar object
sidebar = html.Div(
    [
        html.Button("Zurück zum Netzwerk", id="return-to-full"),
        html.Hr(),
        html.H2(
            "Franz Moufang: The Social Network",
            className="display-4",
            id="sidebar-title",
        ),
        html.Hr(),
        html.P(
            [
                html.P(
                    "Der Graph zeigt das private und berufliche Netzwerk von Franz Moufang, das anhand seiner Gästebücher und Briefe rekonstruiert werden konnte."
                ),
                html.P(
                    "Die Farbverteilung repräsentiert annähernd die verschiedenen Interessen- und Freundesgruppen, die sich im Netzwerk von Franz Moufang entwickelt haben."
                ),
            ],
            className="lead",
            id="sidebar-content",
        ),
    ],
    style=SIDEBAR_STYLE,
    id="info-panel",
)

# The network object
network = html.Div(
    [
        cyto.Cytoscape(
            id="cytoscape-network",
            layout={"name": "preset"},
            minZoom=0.05,
            maxZoom=3,
            style={
                "width": "100%",
                "height": "700px",
                "background-image": "url(/assets/moufang.png)",
                "background-size": "cover",
            },
            elements=nodes + edges,
            stylesheet=[
                {
                    "selector": "node",
                    "style": {
                        "label": "data(label)",
                        "background-color": "data(color)",
                        "width": "data(size)",
                        "height": "data(size)",
                        "font-size": "180px",
                    },
                },
                {
                    "selector": "edge",
                    "style": {
                        "line-color": "data(color)",
                        "width": "8px",
                    },
                },
            ],
        )
    ]
)


@app.callback(
    Output("sidebar-title", "children", allow_duplicate=True),
    Output("sidebar-content", "children", allow_duplicate=True),
    Output("cytoscape-network", "elements", allow_duplicate=True),
    Input("cytoscape-network", "tapNodeData"),
    prevent_initial_call=True,
)
def displayNodeData(data):
    if data:
        filtered_nodes = []
        for node in nodes:
            if node["data"]["id"] in data["neighbors"] + [data["id"]]:
                filtered_nodes.append(node)

        filtered_edges = []
        for edge in edges:
            if edge["data"]["source"] in data["neighbors"] + [data["id"]] and edge[
                "data"
            ]["target"] in data["neighbors"] + [data["id"]]:
                filtered_edges.append(edge)

        content = []

        if "text" in data:
            content.append(html.P([html.B("Kurzinformation: "), data["text"]]))

        if "lebensdaten" in data:
            content.append(html.P([html.B("Lebensdaten: "), data["lebensdaten"]]))

        connections = [html.B("Verbindungen: "), html.Br()]
        for neighbor in filtered_nodes:
            if neighbor["data"]["id"] != data["id"]:
                connections.append(neighbor["data"]["label"] + ", ")
                # connections.append(html.Br())

        content.extend(connections)

        return data["label"], content, filtered_edges + filtered_nodes

    return None, None, nodes + edges


@app.callback(
    Output("info-panel", "children", allow_duplicate=True),
    Output("cytoscape-network", "elements", allow_duplicate=True),
    Input("return-to-full", "n_clicks"),
    prevent_initial_call=True,
)
def return_to_full(n_clicks):
    return sidebar, nodes + edges


app.layout = html.Div([network, sidebar])


if __name__ == "__main__":
    app.run_server(debug=False)
