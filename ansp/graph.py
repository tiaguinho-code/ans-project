import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from math import ceil
import os

def darw_full_graph(path_to_runs, name):
    dfs = {}
    runs = os.listdir(path_to_runs)
    print(runs)
    # runs = [f'{path_to_runs}/{file}' for file in runs]
    visualize_network_graph(path_to_runs, runs, name)


def getnumbers(string):
    numbers = []
    for char in string:
        if char.isdigit():
            numbers.append(int(char))
    result = int(''.join(map(str, numbers)))
    return result
def load_data(base_path, runs):
    dfs = {}
    for run in runs:
        run_number = run.split('.')[0]  
        file_path = base_path + "/" + run
        dfs[run_number] = pd.read_csv(file_path)
        dfs[run_number].drop_duplicates(inplace=True)
    return dfs

def create_graphs(dfs):
    graphs = {}
    layer_mapping = {key: i for i, key in enumerate(dfs.keys())}
    combined_graph = nx.DiGraph()
    
    for key, df in dfs.items():
        G = nx.DiGraph()
        for i in range(len(df) - 1):
            src, tgt = df.iloc[i]['Channel'], df.iloc[i + 1]['Channel']
            G.add_node(src, Training=df.iloc[i]['Training'], layer=layer_mapping[key])
            G.add_node(tgt, Training=df.iloc[i + 1]['Training'], layer=layer_mapping[key])
            if src != tgt:
                G.add_edge(src, tgt)
            #Self-looping
            #else:
            #    G.add_edge(src, tgt, loop=True)
        graphs[key] = G
        combined_graph = nx.compose(combined_graph, G)
    return combined_graph, layer_mapping, graphs

def adjust_graph_layers(combined_graph, layer_mapping):
    total_layers = list(layer_mapping.values())
    median_layer = ceil(np.median(total_layers))
    for node, data in combined_graph.nodes(data=True):
        if data['Training']:
            data['layer'] = median_layer
            
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
        
    minimum_distance = 150
    layers = {layer: [] for layer in layer_mapping.values()}

    # Assign nodes to layers
    for node, data in combined_graph.nodes(data=True):
        layers[data['layer']].append(node)

    # First, sort and adjust within layers
    for layer, nodes in layers.items():
        if not nodes:
            continue
        sorted_nodes = sorted(nodes, key=lambda n: pos[n][1])
        for i in range(1, len(sorted_nodes)):
            current_pos = pos[sorted_nodes[i]][1]
            previous_pos = pos[sorted_nodes[i - 1]][1]
            if current_pos - previous_pos < minimum_distance:
                pos[sorted_nodes[i]] = (pos[sorted_nodes[i]][0], previous_pos + minimum_distance)

    # Handle training and non-training nodes' positions
    training_y_positions = [pos[node][1] for node in combined_graph if combined_graph.nodes[node]['Training']]
    non_training_y_positions = [pos[node][1] for node in combined_graph if not combined_graph.nodes[node]['Training']]

    if training_y_positions:
        min_y_for_training = min(training_y_positions)
    else:
        min_y_for_training = 0  # Default if no training nodes

    if non_training_y_positions:
        max_y_non_training = max(non_training_y_positions)
    else:
        max_y_non_training = 0  # Default if no non-training nodes

    adjustment = min_y_for_training - max_y_non_training - 300

    # Apply adjustments for non-training nodes
    for node, data in combined_graph.nodes(data=True):
        if not data['Training']:
            pos[node] = (pos[node][0], pos[node][1] + adjustment)

    return pos



def visualize_network_graph(base_path, runs, plot_name):
    dfs = load_data(base_path, runs)
    combined_graph, layer_mapping, graphs= create_graphs(dfs)
    pos = adjust_graph_layers(combined_graph, layer_mapping)
    
     # Determine indegrees and assign shapes
    indegrees = combined_graph.in_degree()
    shapes = [' ', 'o', '^', 'd', 'h','p','*'] 
    shape_legend = {}
    for node, deg in indegrees:
        if deg > 0:
            shape = shapes[deg % len(shapes)] if deg < len(shapes) else shapes[-1]
            shape_legend[deg] = shape
        else:
            shape = 'o'
        combined_graph.nodes[node]['shape'] = shape


    plt.figure(figsize=(15, 15))
    colors = [
    'skyblue', 'lightgreen', 'purple', 'red', 'grey', 'pink', 'brown',
    'cyan', 'magenta', 'lime', 'olive', 'chocolate', 'coral', 'lightblue',
    'darkgreen', 'lavender', 'maroon', 'navy', 'goldenrod', 'teal'
    ]

    edge_colors = [
    'blue', 'green', 'purple', 'red', 'darkgrey', 'pink', 'brown',
    'cyan', 'magenta', 'lime', 'olive', 'chocolate', 'coral', 'lightblue',
    'darkgreen', 'lavender', 'maroon', 'navy', 'goldenrod', 'teal'
    ]

    # Draw all nodes first
    for node in combined_graph.nodes():
        node_data = combined_graph.nodes[node]
        color = 'orange' if node_data['Training'] else colors[node_data['layer'] % len(colors)]
        shape = node_data['shape']
        nx.draw_networkx_nodes(combined_graph, pos, nodelist=[node], node_color=color, node_shape=shape, node_size=300, alpha=0.6)

    # Draw the graphs, separating calls by node shape
    for i, (key, graph) in enumerate(graphs.items()):
        nx.draw_networkx_edges(graph, pos, edge_color=edge_colors[i], style='solid', arrows=True)


    # Draw edges
    nx.draw_networkx_labels(combined_graph, pos, font_color='black', font_size=10)

    # Create a sorted list of legend entries based on indegree
    sorted_legend_entries = sorted(shape_legend.items(), key=lambda item: item[0])
    for deg, shape in sorted_legend_entries:
        plt.scatter([], [], c='gray', alpha=0.6, s=100, marker=shape, label=f'Indegree {deg}')

    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, title='Node Shapes')

    plt.title(plot_name)
    plt.axis('off')
    plt.show()
