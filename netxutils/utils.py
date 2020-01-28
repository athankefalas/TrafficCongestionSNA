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
        nodeFirst = edge[0]
        nodeSecond = edge[1]

        if nodeFirst not in nodes:
            nodes.append(nodeFirst)
        if nodeSecond not in nodes:
            nodes.append(nodeSecond)

    return nodes


def betweenness_centrality_critical_nodes(network, critical_edges=None, limit=None, threshold=None):
    critical_nodes = []

    if critical_edges is None:
        critical_edges = []

    for edge in critical_edges:
        nodeFirst = edge[0]
        nodeSecond = edge[1]

        critical_nodes.append(nodeFirst)
        critical_nodes.append(nodeSecond)

    critical_nodes = list(set(critical_nodes))

    if limit is not None:
        if len(critical_nodes) >= limit:
            return critical_nodes

    # find betweenness centrality for all nodes
    betweenness_centralities = nx.betweenness_centrality(network, normalized=True)

    centralities_list = []

    for key in betweenness_centralities.keys():
        centralities_list.append((key, betweenness_centralities[key]))

    centralities_list = sorted(centralities_list, key=lambda pair: pair[1], reverse=True)

    k_limit = len(centralities_list)
    k_threshold = 0.0

    if threshold is not None:
        k_threshold = threshold
    else:
        if len(critical_nodes) > 0:
            centralities = list(map(lambda it: betweenness_centralities[it], critical_nodes))
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
        nodeFirst = edge[0]
        nodeSecond = edge[1]

        critical_nodes.append(nodeFirst)
        critical_nodes.append(nodeSecond)

    critical_nodes = list(set(critical_nodes))

    if limit is not None:
        if len(critical_nodes) >= limit:
            return critical_nodes

    # find betweenness centrality for all nodes
    degree_centralities = nx.degree_centrality(network)

    centralities_list = []

    for key in degree_centralities.keys():
        centralities_list.append((key, degree_centralities[key]))

    centralities_list = sorted(centralities_list, key=lambda pair: pair[1], reverse=True)

    k_limit = len(centralities_list)
    k_threshold = 0.0

    if threshold is not None:
        k_threshold = threshold
    else:
        if len(critical_nodes) > 0:
            centralities = list(map(lambda it: degree_centralities[it], critical_nodes))
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









