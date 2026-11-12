import json
import numpy as np
from itertools import permutations

class TSP_cluster:
    def __init__(self, vertex_names: list, edges: list, root: int):
        self.vertices = vertex_names # list with the indices from the original graph as integers
        self.edges = edges # list of tuples (src, dst, weight)
        self.root = root
        self.n = len(vertex_names)

    def get_optimal():
        def calculate_distance(route, distances):
            return sum(
                distances[route[i], route[i + 1]]
                for i in range(len(route) - 1)
            )

        best_distance = float("inf")
        best_route = None

        # Depot (0) is fixed at the start and end
        for order in permutations(range(1, n)):
            route = (0,) + order + (0,)

            total_distance = calculate_distance(route, distances)

            if total_distance < best_distance:
                best_distance = total_distance
                best_route = route

        print("Optimal route:")
        print(" → ".join(names[i] for i in best_route))
        print(best_route)

        print(f"\nMinimum distance: {best_distance:.2f} km")