import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from math import ceil
import os


def load_data(path_to_runs): 
    runs = os.listdir(path_to_runs)
    dfs = {}
    for run in runs:
        if run.endswith('.csv'):  
            run_number = run.split('.')[0]
            file_path = os.path.join(path_to_runs, run)  
            try:
                df = pd.read_csv(file_path)
                df.drop_duplicates(inplace=True)  
                dfs[run_number] = df
            except Exception as e:
                print(f"Failed to load {run}: {e}")  
    return dfs


def create_graphs(dfs):
    graphs = {}
    layer_mapping = {key: i for i, key in enumerate(dfs.keys())}
    combined_graph = nx.DiGraph()

    # Collect all channels that ever appear as Training=True
    training_channels = set()
    for df in dfs.values():
        training_channels.update(df[df['Training'] == True]['Channel'].unique())

    for key, df in dfs.items():
        G = nx.DiGraph()
        for i in range(len(df) - 1):
            src, tgt = df.iloc[i]['Channel'], df.iloc[i + 1]['Channel']
            # Treat channel as training if it ever appears as training
            src_train = src in training_channels
            tgt_train = tgt in training_channels
            G.add_node(src, Training=src_train, layer=layer_mapping[key])
            G.add_node(tgt, Training=tgt_train, layer=layer_mapping[key])
            if src != tgt:
                G.add_edge(src, tgt)
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
            pos[node] = (layer * 150, pos[node][1] )  
        
    minimum_distance = 150  # Can be adjusted
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
        

    # First pass to find the lowest y-position of training nodes across all layers
    min_y_for_training = float('inf')
    for node, data in combined_graph.nodes(data=True):
        if data['Training'] and pos[node][1] < min_y_for_training:
            min_y_for_training = pos[node][1]

    #Second pass to adjust y-positions for non-training nodes
    adjustment = {}
    for node, data in combined_graph.nodes(data=True):
        if not data['Training']:
            layer = data['layer']
            if layer not in adjustment:
                # Find the highest y-position of non-training nodes in the same layer
                max_y_in_layer = max(pos[n][1] for n in combined_graph.nodes if combined_graph.nodes[n]['layer'] == layer and not combined_graph.nodes[n]['Training'] and np.isfinite(pos[n][1]))
                adjustment[layer] = min_y_for_training - max_y_in_layer - 300
            # Apply adjustment, ensuring all positions are finite
            if np.isfinite(pos[node][1]):
                pos[node] = (pos[node][0], pos[node][1] + adjustment.get(layer, 0))

    # Ensure all positions are finite and adjust if necessary
    for node in pos:
        if not np.isfinite(pos[node][1]):
            # Fallback position if non-finite values found
            pos[node] = (pos[node][0], 0)  
    return pos


def visualize_network_graph(path_to_runs, plot_name):
    dfs = load_data(path_to_runs)
    combined_graph, layer_mapping, graphs= create_graphs(dfs)
    pos = adjust_graph_layers(combined_graph, layer_mapping)
    
     # Determine indegrees and assign shapes
    indegrees = combined_graph.in_degree()
    shapes = [' ', 'o', '^', 'd', 'p','*'] 
    shape_legend = {}
    for node, deg in indegrees:
        if deg > 0:
            shape = shapes[deg % len(shapes)] if deg < len(shapes) else shapes[-1]
            shape_legend[deg] = shape
        else:
            shape = 'o'
        combined_graph.nodes[node]['shape'] = shape


    plt.figure(figsize=(18, 15))
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
    nx.draw_networkx_labels(combined_graph, pos, font_color='black', font_size=9)

    # Create a sorted list of legend entries based on indegree
    sorted_legend_entries = sorted(shape_legend.items(), key=lambda item: item[0])
    for deg, shape in sorted_legend_entries:
        plt.scatter([], [], c='gray', alpha=0.6, s=100, marker=shape, label=f'Indegree {deg}')

    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, title='Node Shapes')

    plt.title(plot_name)
    plt.axis('off')
    plt.show()



def extract_last_titles_and_channels(path_to_runs):
    dfs = load_data(path_to_runs)  # Assume this function loads DataFrames properly
    last_row_info = {}
    sorted_keys = sorted(dfs.keys())  # Sort the keys to maintain a consistent order

    for index, run_number in enumerate(sorted_keys, start=1):
        df = dfs[run_number]
        if not df.empty:
            last_title = df.iloc[-1]['Title']
            last_channel = df.iloc[-1]['Channel']
        else:
            last_title = 'None'
            last_channel = 'None'
        
        # Print directly instead of returning
        print(f"Path{index}:")
        print(f"  Title: {last_title}")
        print(f"  Channel: {last_channel}")
        print() 

