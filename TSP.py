import json
import numpy as np
from itertools import permutations
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit.circuit.library import QAOAAnsatz
from qiskit import transpile
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

def matrix_to_edges(matrix: list):
    edges = []
    for i in range(len(matrix)):
        for j in range(i):
            if matrix[i][j]:
                edges.append((i, j, float(matrix[i][j])))
    return edges

class TSP_cluster:
    def __init__(self, vertex_names: list, edges: list, root: int):
        self.vertex_names = vertex_names # list with the indices from the original graph as integers
        i = 0
        while True: # we set the root to be the first vertex
            if self.vertex_names[i] == root:
                self.vertex_names[0], self.vertex_names[i] = self.vertex_names[i], self.vertex_names[0]
                break
            i += 1

        self.vertex_mapping = {} # mapping from the names to their relative positions
        self.index_mapping = {} # mapping from the indices to their vertex names
        for i,vertex in enumerate(self.vertex_names):
            self.vertex_mapping[vertex] = i
            self.index_mapping[i] = vertex

        self.edges = edges # list of tuples (src, dst, weight)
        self.distances = np.full((len(self.vertex_names), len(self.vertex_names)), 0.0)
        for edge in self.edges:
            self.distances[self.vertex_mapping[edge[0]]][self.vertex_mapping[edge[1]]] = edge[2]
            self.distances[self.vertex_mapping[edge[1]]][self.vertex_mapping[edge[0]]] = edge[2]
        self.n = len(vertex_names)

    def get_optimal(self):
        def calculate_distance(route, distances):
            return sum(
                distances[route[i], route[i + 1]]
                for i in range(len(route) - 1)
            )

        best_distance = float("inf")
        best_route = None

        # Depot (0) is fixed at the start and end
        for order in permutations(range(1, self.n)):
            route = (0,) + order + (0,)

            total_distance = calculate_distance(route, self.distances)

            if total_distance < best_distance:
                best_distance = total_distance
                best_route = route
        best_route_out = [0 for _ in range(len(best_route))]
        for i, vertex in enumerate(best_route):
            best_route_out[i] = self.index_mapping[vertex]
        return best_route_out, float(best_distance)

    def get_route(self, layers: int = 2, visualise: bool = False):
        qp = self._tsp_to_qubo(visualise=visualise)
        H = self._qubo_to_ham(qp, visualise=visualise)
        ansatz = self._build_qaoa_circuit(layers, H, visualise=visualise)
        self._optimise_ham(H, ansatz)

    def _tsp_to_qubo(self, visualise: bool = False):
        m = self.n - 1

        qp = QuadraticProgram("Omniva_TSP")

        m = self.n - 1  # Number of delivery locations

        # Binary variables: x[i, p] = 1 if location i is visited at position p
        for i in range(1, self.n):
            for p in range(m):
                qp.binary_var(name=f"x_{i}_{p}")

        # Objective: minimize total driving distance
        linear = {}
        quadratic = {}

        # Depot -> first delivery
        for i in range(1, self.n):
            linear[f"x_{i}_0"] = self.distances[0, i]

        # Last delivery -> depot
        for i in range(1, self.n):
            name = f"x_{i}_{m-1}"
            linear[name] = linear.get(name, 0) + self.distances[i, 0]

        # Distances between consecutive deliveries
        for p in range(m - 1):
            for i in range(1, self.n):
                for j in range(1, self.n):
                    if i != j:
                        quadratic[(f"x_{i}_{p}", f"x_{j}_{p+1}")] = self.distances[i, j]

        qp.minimize(linear=linear, quadratic=quadratic)

        # Every location must be visited exactly once
        for i in range(1, self.n):
            qp.linear_constraint(
                linear={f"x_{i}_{p}": 1 for p in range(m)},
                sense="==",
                rhs=1,
                name=f"visit_{i}"
            )

        # Every route position must contain exactly one location
        for p in range(m):
            qp.linear_constraint(
                linear={f"x_{i}_{p}": 1 for i in range(1, self.n)},
                sense="==",
                rhs=1,
                name=f"position_{p}"
            )

        if visualise:
            print(qp.prettyprint())
        return qp

    def _qubo_to_ham(self, qp, visualise:bool = False):
        # Convert constrained optimization problem to QUBO
        penalty = 100

        converter = QuadraticProgramToQubo(penalty=penalty)
        qubo = converter.convert(qp)

        # Convert QUBO to Ising Hamiltonian
        H_raw, offset = qubo.to_ising()

        # Scale Hamiltonian
        H = (H_raw / penalty).simplify()

        if visualise:
            print("QUBO variables:", qubo.get_num_binary_vars())
            print("Qubits:", H.num_qubits)
            print("Hamiltonian terms:", len(H))
        return H

    def _build_qaoa_circuit(self, p, H, visualise: bool = False):
        REPS = p

        ansatz = QAOAAnsatz(
            cost_operator=H,
            reps=REPS
        )

        # Transpile to basic gates for statevector simulation
        ansatz = transpile(
            ansatz,
            basis_gates=["h", "rx", "rz", "cx"],
            optimization_level=1
        )

        if visualise:
            print("Qubits:", ansatz.num_qubits)
            print("Parameters:", ansatz.num_parameters)
            print("Circuit depth:", ansatz.depth())

        return ansatz

    def _optimise_ham(self, H, ansatz, visualise: bool = False):
        # Hamiltonian used for optimization
        H_matrix = H

        def qaoa_cost(params):
            # Assign gamma and beta values
            circuit = ansatz.assign_parameters(params)

            # Simulate quantum circuit
            state = Statevector.from_instruction(circuit)

            # Calculate expected energy
            energy = np.real(state.expectation_value(H_matrix))

            return energy

        # Initial parameters
        initial_params = np.full(ansatz.num_parameters, 0.5)

        # Optimize QAOA parameters
        result = minimize(
            qaoa_cost,
            initial_params,
            method="COBYLA",
            options={"maxiter": 200}
        )
        if visualise:
            print("Optimization finished!")
            print("Optimal parameters:", result.x)
            print("Minimum energy:", result.fun)
            print("Iterations:", result.nfev)

        return result



# 1. Simulate the optimized QAOA circuit
optimized_circuit = ansatz.assign_parameters(result.x)
state = Statevector.from_instruction(optimized_circuit)
probabilities = state.probabilities()

# 2. Generate all valid TSP routes
valid_routes = []

for order in permutations(range(1, n)):
    route = (0,) + order + (0,)

    # Encode the route into binary variables
    assignment = {
        f"x_{i}_{p}": int(order[p] == i)
        for i in range(1, n)
        for p in range(m)
    }

    bits = np.array([
        assignment[var.name]
        for var in qp.variables
    ])

    # Convert binary variables to statevector index
    index = sum(int(bit) << i for i, bit in enumerate(bits))

    probability = probabilities[index]
    distance = calculate_distance(route, distances)

    valid_routes.append((route, distance, probability))

# 3. Calculate total valid-route probability
valid_probability = sum(
    probability
    for route, distance, probability in valid_routes
)

# 4. Calculate optimal-route probability
optimal_probability = sum(
    probability
    for route, distance, probability in valid_routes
    if np.isclose(distance, best_distance)
)

# 5. Find the most probable VALID route
best_qaoa_route = max(
    valid_routes,
    key=lambda item: item[2]
)

# 6. Print results
print("=== QAOA RESULTS ===")
print(f"Classical optimum: {best_distance:.3f} km")
print(f"Valid route probability: {valid_probability * 100:.4f}%")
print(f"Optimal route probability: {optimal_probability * 100:.4f}%")

print("\nMost probable valid route:")
print(" -> ".join(map(str, best_qaoa_route[0])))
print(f"Distance: {best_qaoa_route[1]:.3f} km")
print(f"Probability: {best_qaoa_route[2] * 100:.4f}%")

if __name__ == "__main__":
    vertices = [4, 5, 8, 2, 1]
    edges = [(4,5,1),
             (4,8,2),
             (4,2,3),
             (4,1,4),
             (5,8,1),
             (5,2,8),
             (5,1,11),
             (8,2,1),
             (8,1,10),
             (2,1,3)]
    tsp = TSP_cluster(vertices, edges, 2)
    print(tsp.get_optimal())
    print(tsp.distances)