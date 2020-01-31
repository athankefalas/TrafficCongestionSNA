import networkx as nx


def load_toyroad():
    network = nx.readwrite.read_adjlist("./data/toy/toyroad.edges",
                                        comments="%",
                                        create_using=nx.Graph)
    network.name = "Toy Roads"
    return network


def load_euroroad():
    network = nx.readwrite.read_adjlist("./data/euroroad/road-euroroad.edges",
                                        comments="%",
                                        create_using=nx.Graph)
    network.name = "Euro Roads"
    return network


def load_italyroad():
    network = nx.readwrite.read_adjlist("./data/italyroad/road-italy-osm.edges",
                                        comments="%",
                                        create_using=nx.Graph)
    network.name = "Italy Roads"
    return network


def load_minessotaroad():
    network = nx.readwrite.read_adjlist("./data/minnesotaroad/road-minnesota.mtx",
                                        comments="%",
                                        create_using=nx.Graph)
    network.name = "Minnesota Roads"
    return network


def largest_connected_component(network):
    connected_components = list(nx.connected_components(network))
    connected_components.sort(key=len)

    return nx.subgraph(network, connected_components[-1])


def nodes_from_edges(edges):
    nodes = []

    for edge in edges:
        node_first = edge[0]
        node_second = edge[1]

        if node_first not in nodes:
            nodes.append(node_first)
        if node_second not in nodes:
            nodes.append(node_second)

    return nodes


def betweenness_centrality_critical_nodes(network, critical_edges=None, limit=None, threshold=None):
    critical_nodes = []

    if critical_edges is None:
        critical_edges = []

    for edge in critical_edges:
        node_first = edge[0]
        node_second = edge[1]

        critical_nodes.append(node_first)
        critical_nodes.append(node_second)

    critical_nodes = list(set(critical_nodes))

    if limit is not None:
        if len(critical_nodes) >= limit:
            return critical_nodes

    # find betweenness centrality for all nodes
    all_betweenness_centralities = nx.betweenness_centrality(network, normalized=True)

    centralities_list = []

    for key in all_betweenness_centralities.keys():
        centralities_list.append((key, all_betweenness_centralities[key]))

    centralities_list = sorted(centralities_list, key=lambda pair: pair[1], reverse=True)

    k_limit = len(centralities_list)
    k_threshold = 0.0

    if threshold is not None:
        k_threshold = threshold
    else:
        if len(critical_nodes) > 0:
            centralities = list(map(lambda it: all_betweenness_centralities[it], critical_nodes))
            centralities.sort()
            k_threshold = centralities[-1]
        else:
            k_threshold = 0.0

    if limit is not None:
        k_limit = limit

    for node_centrality_pair in centralities_list:
        if len(critical_nodes) >= k_limit:
            break

        node = node_centrality_pair[0]
        centrality = node_centrality_pair[1]

        if centrality < k_threshold:
            continue

        if node in critical_nodes:
            continue

        critical_nodes.append(node)

    # for node in critical_nodes:
    #     print("Node:", node, "Betweenness Centrality:", betweenness_centralities[node])

    return critical_nodes


def degree_centrality_critical_nodes(network, critical_edges=None, limit=None, threshold=None):
    critical_nodes = []

    if critical_edges is None:
        critical_edges = []

    for edge in critical_edges:
        node_first = edge[0]
        node_second = edge[1]

        critical_nodes.append(node_first)
        critical_nodes.append(node_second)

    critical_nodes = list(set(critical_nodes))

    if limit is not None:
        if len(critical_nodes) >= limit:
            return critical_nodes

    # find betweenness centrality for all nodes
    all_degree_centralities = nx.degree_centrality(network)

    centralities_list = []

    for key in all_degree_centralities.keys():
        centralities_list.append((key, all_degree_centralities[key]))

    centralities_list = sorted(centralities_list, key=lambda pair: pair[1], reverse=True)

    k_limit = len(centralities_list)
    k_threshold = 0.0

    if threshold is not None:
        k_threshold = threshold
    else:
        if len(critical_nodes) > 0:
            centralities = list(map(lambda it: all_degree_centralities[it], critical_nodes))
            centralities.sort()
            k_threshold = centralities[-1]
        else:
            k_threshold = 0.0

    if limit is not None:
        k_limit = limit

    for node_centrality_pair in centralities_list:
        if len(critical_nodes) >= k_limit:
            break

        node = node_centrality_pair[0]
        centrality = node_centrality_pair[1]

        if centrality < k_threshold:
            continue

        if node in critical_nodes:
            continue

        critical_nodes.append(node)

    # for node in critical_nodes:
    #     print("Node:", node, "Degree Centrality:", degree_centralities[node])

    return critical_nodes


def min_degree(graph):
    all_degrees = nx.degree(graph)

    min_deg = len(nx.nodes(graph)) - 1

    for node_degree_pair in all_degrees:
        degree = node_degree_pair[1]

        if degree < min_deg:
            min_deg = degree

    return min_deg


def max_degree(graph):
    all_degrees = nx.degree(graph)

    max_deg = 0

    for node_degree_pair in all_degrees:
        degree = node_degree_pair[1]

        if degree > max_deg:
            max_deg = degree

    return max_deg


def betweenness_centralities(graph):
    return nx.betweenness_centrality(graph, normalized=True)


def degree_centralities(graph):
    return nx.degree_centrality(graph)


def degrees(graph):
    all_degrees = nx.degree(graph)
    degrees_map = dict()

    for node_degree_pair in all_degrees:
        node = node_degree_pair[0]
        degree = node_degree_pair[1]
        degrees_map[node] = degree

    return degrees_map
