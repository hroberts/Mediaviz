import sys
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from fa2l import force_atlas2_layout
import networkx as nx
import matplotlib.pyplot as plt

from adjustText import adjust_text

from utils import set_node_size, set_node_color, set_node_label, edgecolor_by_source,filter_graph, get_subgraph_pos
# from scaling import extract_correct_scale

def main():
    if len(sys.argv) < 2:
        sys.exit('usage: %s < input gexf' % sys.argv[0])

    # Input Graph file 

    infile = sys.argv[1]

    G = nx.read_gexf(infile)
    
    # extract the largest weakly connected component and convert to undirected for fa2l
    
    G = max(nx.weakly_connected_component_subgraphs(G), key=len).to_undirected()
    
    # set parameters
    
    colormap = {'null': 'lightgray',
         'partisan_2012_conservative': 'r',
         'partisan_2012_liberal': 'b',
         'partisan_2012_libertarian': 'y'}
    color_field = "partisan_code"
    size_field = 'inlink_count'
    filter_field = "inlink_count"
    label_field = "label"
    num_labels = 20 # number of labels to visualize
    k = 100 # number of nodes to visualize

    # If the size of Graph > 1000 nodes, set G to the subgraph containing largest 1000 nodes to get the layout
    
    if len(G.nodes()) > 1000:
        G = filter_graph(G,filter_by=filter_field,top=1000).to_undirected()

    # extract the positions
    
    pos = force_atlas2_layout(
        G,
        iterations=50,
        pos_list=None,
        node_masses=None,
        outbound_attraction_distribution=True,
        lin_log_mode=True,
        prevent_overlapping=True,
        edge_weight_influence=1.0,

        jitter_tolerance=1.0,
        barnes_hut_optimize=True,
        barnes_hut_theta=0.5,

        scaling_ratio=38,
        strong_gravity_mode=False,
        multithread=False,
        gravity=1.0)
    
    print("Extracted the positions")
    print(pos)

    # Extract top 500 nodes for visualization
    top_k_subgraph = filter_graph(G,filter_by=filter_field,top=k).to_undirected()

    # Set visual attributes
    
    node_colors = set_node_color(top_k_subgraph,color_by=color_field,colormap=colormap)
    node_sizes = set_node_size(top_k_subgraph,size_field= "inlink_count",min_size = 0.1, max_size=800)
    node_labels = set_node_label(top_k_subgraph,label = label_field)
    subgraph_pos = get_subgraph_pos(top_k_subgraph,pos)
    edge_colors = edgecolor_by_source(top_k_subgraph,node_colors)
    
    print("Drawing the visualization")
    
    # Get specific labels
    
    subset_label_nodes = sorted(zip(top_k_subgraph.nodes(),node_sizes), key= lambda x:x[1], reverse = True)[0:num_labels]
    subset_labels = {n[0]:node_labels[n[0]] for n in subset_label_nodes}
    
    # plot the visualization
    
    fig = plt.figure(figsize=(10,10),dpi=100)
    ax = fig.add_subplot(111)
    #ax.set(xlim=[0.0, 1.0], ylim=[0.0, 1.0], title='Network Viz')


    # Draw the nodes, edges, labels separately 
    
    nodes = nx.draw_networkx_nodes(top_k_subgraph,pos=subgraph_pos,node_size=node_sizes,node_color=node_colors,                                            alpha=.7);    
    edges = nx.draw_networkx_edges(top_k_subgraph,pos=subgraph_pos,edge_color=edge_colors,alpha=0.01);
    labels = nx.draw_networkx_labels(top_k_subgraph,pos=subgraph_pos,labels=subset_labels, font_size=8);

    # Adjust label overlapping
    
    
    x_pos = [v[0] for k,v in subgraph_pos.items()]
    y_pos = [v[1] for k,v in subgraph_pos.items()]
    adjust_text(texts = list(labels.values()), x = x_pos, y = y_pos,arrowprops=dict(arrowstyle='->', color='lightgray'))

    # Declutter visualization

    #ax.axis("off");
    
    # save the plot
    
    plt.savefig("1.png")
    
    # Show the plot
    plt.show()

    
main()
