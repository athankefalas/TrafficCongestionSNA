import networkx as nx
import netxutils.utils as u

def run_road_congestion():
    print("Road congestion.")
    road_net = u.load_toyroad()

    # if loaded net is not connected get the largest
    # connected component as a sub-graph
    if not nx.is_connected(road_net):
        road_net = u.largest_connected_component(road_net)

    print("|----\tLoaded network info\t----|")
    print(nx.info(road_net))

    roads_clustering_oeff = nx.average_clustering(road_net)
    print("Clustering coeff:", roads_clustering_oeff)

    roads_transitivity = nx.transitivity(road_net)
    print("Transitivity:", roads_transitivity)

    bridge_nodes = u.nodes_from_edges(list(nx.bridges(road_net)))
    betweenness_centrality_critical_nodes = u.betweenness_centrality_critical_nodes(road_net, limit=len(bridge_nodes))
    degree_centrality_nodes = u.degree_centrality_critical_nodes(road_net, limit=len(bridge_nodes))

    critical_nodes = set(bridge_nodes).intersection(betweenness_centrality_critical_nodes, degree_centrality_nodes)

    for node in critical_nodes:
        print("Critical node:", node)

    print("")
# EOF
