import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from math import ceil
import os

def getnumbers(string):
    numbers = []
    for char in string:
        if char.isdigit():
            numbers.append(int(char))
    result = int(''.join(map(str, numbers)))
    return result


def draw(path_to_runs):
    runs = os.listdir(path_to_runs)
    runs = [f'{path_to_runs}/{file}' for file in runs]
    print(runs)
    # Create a dictionary to hold the dataframes
    dfs = {}

    # Load each file into the dictionary
    for run in runs:
        run_number = getnumbers(run)  # This will extract the part of the filename without '.csv'
        dfs[run_number] = pd.read_csv(run)

    graphs = {}
    layer_mapping = {key: i for i, key in enumerate(dfs.keys())}

    # Create graphs for each DataFrame, avoiding self-loops and assigning initial layers
    for key, df in dfs.items():
        G = nx.DiGraph()
        current_layer = layer_mapping[key]
        for i in range(len(df) - 1):
            src = df.iloc[i]['Channel']
            tgt = df.iloc[i + 1]['Channel']
            if src != tgt:
                G.add_node(src, Training=df.iloc[i]['Training'], layer=current_layer)
                G.add_node(tgt, Training=df.iloc[i + 1]['Training'], layer=current_layer)
                G.add_edge(src, tgt)
        graphs[key] = G

    # Combine all individual graphs into a single graph
    combined_graph = nx.compose_all(graphs.values())

    # Calculate the median layer to position 'Training' nodes
    total_layers = list(layer_mapping.values())
    median_layer = ceil(np.median(total_layers))

    # Update the layer for nodes where 'Training' is True to the median layer
    for node, data in combined_graph.nodes(data=True):
        if data.get('Training'):
            data['layer'] = median_layer

    # Apply a hierarchical layout using 'dot'
    pos = graphviz_layout(combined_graph, prog='dot')

    # Spread nodes in the same adjusted layer horizontally to emphasize parallel paths
    layers = {}

    for node, data in combined_graph.nodes(data=True):
        layer = data['layer']
        if layer not in layers:
            layers[layer] = []
        layers[layer].append(node)

    for layer, nodes in layers.items():
        for i, node in enumerate(nodes):
            pos[node] = (layer * 100, pos[node][1] )  


    minimum_distance=100
    # Sorting nodes in each layer by their y-position and adjusting positions if too close
    for layer, nodes in layers.items():
        sorted_nodes = sorted(nodes, key=lambda n: pos[n][1])
        for i in range(1, len(sorted_nodes)):
            current_pos = pos[sorted_nodes[i]][1]
            previous_pos = pos[sorted_nodes[i - 1]][1]
            if current_pos - previous_pos < minimum_distance:
                pos[sorted_nodes[i]] = (pos[sorted_nodes[i]][0], previous_pos + minimum_distance)

    # First pass to find the lowest y-position of training nodes across all layers
    min_y_for_training = float('inf')
    for node, data in combined_graph.nodes(data=True):
        if data['Training'] and pos[node][1] < min_y_for_training:
            min_y_for_training = pos[node][1]

    # Second pass to adjust y-positions for non-training nodes
    adjustment = {}
    for node, data in combined_graph.nodes(data=True):
        if not data['Training']:
            layer = data['layer']
            if layer not in adjustment:
                # Find the highest y-position of non-training nodes in the same layer
                max_y_in_layer = max(pos[n][1] for n in combined_graph.nodes if combined_graph.nodes[n]['layer'] == layer and not combined_graph.nodes[n]['Training'])
                adjustment[layer] = min_y_for_training-300 - max_y_in_layer
            # Apply adjustment
            pos[node] = (pos[node][0], pos[node][1] + adjustment[layer])


    # Indegree calculation
    indegree_map = dict(combined_graph.in_degree())

    # Shapes for different indegrees
    shapes = [ '','o','^', 's', 'p', '*', 'h', 'H', 'D', 'd', '|', '_']
    # Mapping indegrees to shapes dynamically
    unique_indegrees = sorted(set(indegree_map.values()))
    indegree_to_shape = {deg: shapes[i % len(shapes)] for i, deg in enumerate(unique_indegrees) if deg > 1}

    # Assign shapes based on indegree
    node_shapes = {node: indegree_to_shape.get(indegree, 'o') for node, indegree in indegree_map.items()}


    plt.figure(figsize=(15, 15))
    colors = ['skyblue', 'lightgreen', 'purple', 'red', 'grey', 'pink', 'brown']
    edge_colors = ['blue', 'green', 'purple', 'red', 'darkgrey', 'pink', 'brown']


    # Draw all nodes first
    for node in combined_graph.nodes():
        node_data = combined_graph.nodes[node]
        color = 'orange' if node_data['Training'] else colors[node_data['layer'] % len(colors)]
        shape = node_shapes[node]
        nx.draw_networkx_nodes(combined_graph, pos, nodelist=[node], node_color=color, node_shape=shape, node_size=300, alpha=0.6)

    # Draw the graphs, separating calls by node shape
    for i, (key, graph) in enumerate(graphs.items()):
        nx.draw_networkx_edges(graph, pos, edge_color=edge_colors[i], style='solid', arrows=True)


    # Draw edges
    nx.draw_networkx_labels(combined_graph, pos, font_color='black', font_size=10)

    plt.title('Network Graph with Highlighted Nodes')
    plt.axis('off')
    plt.show()
