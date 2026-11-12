import json
import numpy as np
import TSP

with open("tallinn_osrm_matrix.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Number of locations, including depot
n = 5

# Location names
names = [point["name"] for point in data["points"][:n]]

# Distance matrix in kilometres
distances = np.array(data["distances"], dtype=float)[:n, :n] / 1000
for i in range(len(distances)):
    for j in range(i):
        distances[i][j]=distances[j][i]
        
print("Locations:")
for i, name in enumerate(names):
    print(f"{i}: {name}")

print("\nDistance matrix (km):")
print(np.round(distances, 2))

edges = TSP.matrix_to_edges(distances)

tsp = TSP.TSP_cluster(vertex_names=[i for i in range(n)], edges=edges, root=0)
print(tsp.get_optimal())
print(tsp.edges)
qp = tsp.tsp_to_qubo()