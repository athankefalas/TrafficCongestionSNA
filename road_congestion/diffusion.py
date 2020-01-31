import numpy as np
import networkx as nx


def uniform_rand_probability(edge):
    return np.random.uniform(0.0, 1.0)


def multinomial_rand_probability(edge):
    max = np.random.multinomial(1, [1 / 100] * 100).argmax()
    return max * 0.01


def decreasing_cascade(graph, seed_nodes, max_iter=None, diffusion_probability_generator=None):
    diff_probas = dict()

    if diffusion_probability_generator is not None:
        if not callable(diffusion_probability_generator):
            raise AssertionError("Paramater diffusion_probability_generator is not callable.")
    else:
        diffusion_probability_generator = uniform_rand_probability

    if max_iter is None:
        max_iter = min(len(nx.edges(graph)), 100)

    for edge in nx.edges(graph):
        node_one = edge[0]
        node_other = edge[1]

        diffusion_prob = diffusion_probability_generator(edge)

        if node_one not in diff_probas.keys():
            diff_probas[node_one] = dict()

        node_one_probs = diff_probas[node_one]
        node_one_probs[node_other] = diffusion_prob
        diff_probas[node_one] = node_one_probs

    # print("Starting...")
    affected = set(seed_nodes)

    active = set(seed_nodes)
    inactive = set()
    visited_nodes = list()
    step = 1

    while True:
        if step > max_iter:
            break

        active, inactive, visited_nodes = __decreasing_cascade_diffuse__(graph, active, inactive,
                                                                         visited_nodes, diff_probas)
        step += 1

        affected = affected.union(active)

        if len(active) == 0:
            break

    return affected


def __decreasing_cascade_diffuse__(graph, active, inactive, visited_nodes, diffusion_probabilities):
    if visited_nodes is None:
        visited_nodes = []

    activated_nodes = set()

    for active_node in set(active):
        neighbours = set(graph.successors(active_node))
        susceptible_neighbours = neighbours.difference(active)\
                                           .difference(inactive)\
                                           .difference(activated_nodes)

        for susceptible_node in susceptible_neighbours:
            # should never ever be true, sanity check
            if susceptible_node in active or susceptible_node in inactive:
                continue

            decrease_factor = visited_nodes.count(susceptible_node) + 1
            diffusion_prob = diffusion_probabilities[active_node][susceptible_node] / decrease_factor
            activation_prob = np.random.uniform(0.0, 1.0)

            visited_nodes.append(susceptible_node)
            activation = activation_prob >= (1.0-diffusion_prob)

            if activation:
                activated_nodes.add(susceptible_node)

    inactive = inactive.union(active)
    active = set(activated_nodes)

    return active, inactive, visited_nodes
