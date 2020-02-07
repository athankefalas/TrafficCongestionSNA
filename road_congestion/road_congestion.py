import itertools as itools
import networkx as nx
import netxutils.utils as u
import road_congestion.diffusion as diffuse
from road_congestion.graph_entity_info import nodes_edge_info

min_degree = 0
max_degree = 0
bridge_nodes = list()
edges_info = dict()


def run_road_congestion():
    print("Road congestion analysis using Social Network Analysis.")
    print("")  # console padding

    # !!! WARNING !!!
    #
    # If you decide to use italy-road
    # make sure to change iter_count in
    # influence max and min method calls
    # to a small number, even to 1.
    #
    # Also it is possible depending on the
    # host machine, to receive an out of
    # memory error.

    # Load road network
    # road_net = u.load_minessotaroad()
    # road_net = u.load_toyroad()
    road_net = u.load_toyroad()

    # if loaded road network is not connected get the largest
    # connected component as a sub-graph
    if not nx.is_connected(road_net):
        road_net = u.largest_connected_component(road_net)

    print("Loaded", road_net.name, "dataset.")

    print("")  # console padding

    print("Identifying high priority intersections...")
    global bridge_nodes
    bridge_nodes = u.nodes_from_edges(list(nx.bridges(road_net)))
    betweenness_centrality_critical_nodes = u.betweenness_centrality_critical_nodes(road_net, limit=len(bridge_nodes))
    degree_centrality_nodes = u.degree_centrality_critical_nodes(road_net, limit=len(bridge_nodes))

    critical_nodes = set(bridge_nodes).intersection(betweenness_centrality_critical_nodes, degree_centrality_nodes)

    critical_nodes_count = len(critical_nodes)
    for node in critical_nodes:
        print("High priority intersection:", node)

    print("")  # just some console padding

    # convert to directed graph for diffusion
    if not road_net.is_directed():
        road_net = road_net.to_directed()

    # find and cache the min and max degrees
    global min_degree, max_degree
    min_degree = u.min_degree(road_net)
    max_degree = u.max_degree(road_net)

    # find and cache info for all edges
    global edges_info
    edges_info = edges_info_map(road_net)

    nodes = list(set(nx.nodes(road_net)))

    # get infectiousness map for all nodes
    # infectiousness_map = node_infectiousness(road_net, nodes, max_iter=1000)

    # Number of iterations for diffusing using a specific set of seeds
    # the diffusion potential is averaged from each iteration to avoid
    # randomly optimal seeds. The larger the number of iterations the
    # highest accuracy of the result.
    iter_n = 100

    print("Finding optimal intersections to handle high traffic...")
    optimal_max = maximize_diffusion(road_net, nodes, critical_nodes_count, iter_count=iter_n)

    # print the influence max/minimization results and affected nodes
    print("Low traffic when congestion starts from:", optimal_max)
    affected = diffuse.decreasing_cascade(road_net, optimal_max, diffusion_probability_generator=diffusion_probability)
    affected_percentage = (len(affected)/len(nodes)) * 100
    print("Affected", affected_percentage, "% of nodes. Affected:", affected)

    print("")  # console padding

    print("Finding worst intersections to handle high traffic...")
    optimal_min = minimize_diffusion(road_net, nodes, critical_nodes_count, iter_count=iter_n)

    print("High traffic when congestion starts from:", optimal_min)
    affected = diffuse.decreasing_cascade(road_net, optimal_min, diffusion_probability_generator=diffusion_probability)
    affected_percentage = (len(affected) / len(nodes)) * 100
    print("Affected", affected_percentage, "% of nodes. Affected:", affected)

    print("Common nodes:", set(optimal_max).intersection(optimal_min))

    print("")  # console padding

    print("Finding propagation ability of high priority nodes...")
    affected_percentage_avg = avg_diffusion_potential(road_net, list(critical_nodes), iter_count=iter_n)
    print("Average diffusion potential:", affected_percentage_avg)


def edges_info_map(graph):
    edge_infos = dict()

    degrees = u.degrees(graph)
    betweeness_centr = u.betweenness_centralities(graph)
    degree_centr = u.degree_centralities(graph)

    for edge in nx.edges(graph):
        node_one = edge[0]
        node_other = edge[1]

        edge_info = nodes_edge_info(node_one, node_other, degrees, betweeness_centr, degree_centr)

        if node_one not in edge_infos.keys():
            edge_infos[node_one] = dict()

        node_one_edges_info = edge_infos[node_one]
        node_one_edges_info[node_other] = edge_info
        edge_infos[node_one] = node_one_edges_info

    return edge_infos


def flow_factor(node_info):
    # node = node_info.node
    # degree = node_info.degree
    betweenness_centrality = node_info.betweenness_centrality
    degree_centrality = node_info.degree_centrality

    # Flow is weighted half by degree centrality and half by betweenness centrality.
    # A higher degree centrality is a higher chance to be able to handle traffic.
    # A high betweenness centrality may indicate a congestion point in
    # the road network, as most paths may use the node.
    flow = (degree_centrality / 2.0) + ((1.0 - betweenness_centrality) / 2.0)

    return flow


def diffusion_probability(edge):
    # get the cached edge info
    origin = edge[0]
    destination = edge[1]
    edge_info = edges_info[origin][destination]

    # get the info for both nodes
    origin_info = edge_info.first_node_info
    destination_info = edge_info.second_node_info

    # find the flow value for each node
    origin_flow = flow_factor(origin_info)
    destination_flow = flow_factor(destination_info)

    # find a baseline flow avg to use for finding the penalty value
    flow = (origin_flow + destination_flow) / 2.0
    degree_delta = abs(origin_info.degree - destination_info.degree)
    # the penalty is calculated with the avg flow of the 2 nodes
    # relative to the max degree in the network
    # (this is a bit of an ad-hoc solution)
    penalty = flow / max_degree

    if origin_info.degree < destination_info.degree:  # malus, traffic in busier destination intersection
        destination_flow -= (penalty * degree_delta)
    elif origin_info.degree > destination_info.degree:
        if destination_info.node in bridge_nodes:  # malus, destination is a possible choke point
            destination_flow -= (penalty * degree_delta)
        else:  # malus, origin is busier
            origin_flow -= penalty
    elif origin_info.degree == destination_info.degree:  # malus, busier roads will have larger congestion
        origin_flow -= (penalty * origin_info.degree)

    # calculate the new average of the penalized origin flow and destination flow
    flow = (origin_flow + destination_flow) / 2.0

    # debug
    # print("Flow of ", edge_info.describe(), ":", flow)

    return flow


def avg_diffusion_potential(road_net, seeds, iter_count=100):
    # find the set of seeds that maximizes the diffusion
    affected_avg = 0.0

    for n in range(0, iter_count):
        affected = diffuse.decreasing_cascade(road_net, list(seeds),
                                              diffusion_probability_generator=diffusion_probability)
        affected_avg += len(affected)

    affected_avg = affected_avg / iter_count

    return affected_avg/len(nx.nodes(road_net))


def node_infectiousness(road_net, nodes, max_iter=100, verbose=False):
    infectiousness_map = dict()

    for idx in range(0, len(nodes)):
        node = nodes[idx]
        count_sum = 0

        for n in range(0, max_iter):
            affected = diffuse.decreasing_cascade(road_net, [node],
                                                  diffusion_probability_generator=diffusion_probability)
            count_sum += len(affected)

        infectiousness = (count_sum / float(max_iter))

        infectiousness_map[node] = infectiousness

        if verbose:
            print("Node", node, "affected:", infectiousness, "nodes on average.")

    return infectiousness_map


def maximize_diffusion(road_net, nodes, budget, iter_count=100):
    candidate_seeds = set()

    # get sets of candidate seeds
    for combination in itools.combinations(nodes, budget):
        seeds = set(combination)

        if len(seeds) != budget:
            continue

        candidate_seeds.add(tuple(seeds))

    max_affected = budget
    optimal_seeds = tuple()

    # find the set of seeds that maximizes the diffusion
    for seeds in candidate_seeds:
        affected_avg = 0.0

        for n in range(0, iter_count):
            affected = diffuse.decreasing_cascade(road_net, list(seeds),
                                                  diffusion_probability_generator=diffusion_probability)
            affected_avg += len(affected)

        affected_avg = affected_avg / iter_count

        if affected_avg >= max_affected:
            max_affected = affected_avg
            optimal_seeds = seeds

    return list(optimal_seeds)


def minimize_diffusion(road_net, nodes, budget, iter_count=100):
    candidate_seeds = set()

    # get sets of candidate seeds
    for combination in itools.combinations(nodes, budget):
        seeds = set(combination)

        if len(seeds) != budget:
            continue

        candidate_seeds.add(tuple(seeds))

    min_affected = len(nodes)
    optimal_seeds = tuple()

    # find the set of seeds that minimizes the diffusion
    for seeds in candidate_seeds:
        affected_avg = 0.0

        for n in range(0, iter_count):
            affected = diffuse.decreasing_cascade(road_net, list(seeds),
                                                  diffusion_probability_generator=diffusion_probability)
            affected_avg += len(affected)

        affected_avg = affected_avg / iter_count

        if affected_avg <= min_affected:
            min_affected = affected_avg
            optimal_seeds = seeds

    return list(optimal_seeds)

# EOF
