class EdgeInfo:
    edge = None
    first_node_info = None
    second_node_info = None

    def __init__(self, first_node_info, second_node_info):
        self.edge = (first_node_info.node, second_node_info.node)
        self.first_node_info = first_node_info
        self.second_node_info = second_node_info

    def __repr__(self):
        return "["+str(self.first_node_info)+" -> "+str(self.second_node_info)+"]"

    def describe(self):
        return "["+str(self.first_node_info.node)+" -> "+str(self.second_node_info.node)+"]"


class NodeInfo:
    node = None
    degree = 0.0
    betweenness_centrality = 0.0
    degree_centrality = 0.0

    def __init__(self, node, degree, betweenness_centrality, degree_centrality):
        self.node = node
        self.degree = degree
        self.betweenness_centrality = betweenness_centrality
        self.degree_centrality = degree_centrality

    def __repr__(self):
        return "{" + str(self.node) + " (" + str(self.degree) + ", " + str(self.betweenness_centrality) \
               + ", " + str(self.degree_centrality) + ") }"


def node_info(node, degrees_map, betweenness_centr_map, degree_centr_map):
    degree = degrees_map[node]
    betweenness_centrality = betweenness_centr_map[node]
    degree_centrality = degree_centr_map[node]
    return NodeInfo(node, degree, betweenness_centrality, degree_centrality)


def edge_info(edge, degrees_map, betweenness_centr_map, degree_centr_map):
    node_one_info = node_info(edge[0], degrees_map, betweenness_centr_map, degree_centr_map)
    node_other_info = node_info(edge[1], degrees_map, betweenness_centr_map, degree_centr_map)
    return EdgeInfo(node_one_info, node_other_info)


def nodes_edge_info(node_one, node_other, degrees_map, betweenness_centr_map, degree_centr_map):
    node_one_info = node_info(node_one, degrees_map, betweenness_centr_map, degree_centr_map)
    node_other_info = node_info(node_other, degrees_map, betweenness_centr_map, degree_centr_map)
    return EdgeInfo(node_one_info, node_other_info)

# EOF
