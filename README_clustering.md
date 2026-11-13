# Clustered TSP with QAOA (asymmetric distances)

This README describes `tsp_clustering.ipynb`. The notebook plans one delivery route through **10 real locations in Tallinn**. It starts and ends at the Omniva depot.

Solving all 10 locations with QAOA in one piece would need 81 qubits, which is far beyond what we can simulate. The notebook therefore splits the problem into small sub-problems of at most 9 qubits. It solves each one with QAOA and joins the results into one route.

All QAOA building blocks come from the shared library notebook `tsp_library.ipynb`.

---

## Contents

1. [Results at a glance](#1-results-at-a-glance)
2. [Files](#2-files)
3. [Setup and running](#3-setup-and-running)
4. [The pipeline](#4-the-pipeline)
5. [How one sub-problem is solved with QAOA](#5-how-one-sub-problem-is-solved-with-qaoa)
6. [Notebook walkthrough](#6-notebook-walkthrough)
7. [Configuration](#7-configuration)
8. [Interpreting the results](#8-interpreting-the-results)
9. [Limitations and next steps](#9-limitations-and-next-steps)

---

## 1. Results at a glance

Run with the default configuration (10 locations, 3 clusters, asymmetric distances, p = 2 QAOA layers, ideal simulator, 10 000 shots):

| Sub-problem | Locations | Qubits | Route found by QAOA | Length | Classical optimum |
|---|---|---|---|---|---|
| Central graph | 0, 1, 6, 2 | 9 | 0 → 1 → 6 → 2 → 0 | 26.931 km | 26.931 km ✓ |
| Cluster of 1 | 1, 3, 4, 5 | 9 | 1 → 3 → 4 → 5 → 1 | 10.109 km | 10.109 km ✓ |
| Cluster of 6 | 6, 7, 8 | 4 | 6 → 8 → 7 → 6 | 9.557 km | 9.557 km ✓ |
| Cluster of 2 | 2, 9 | – | 2 → 9 → 2 (only possible route) | 6.242 km | 6.242 km ✓ |

**Final route:** `0 → 1 → 3 → 4 → 5 → 1 → 6 → 8 → 7 → 6 → 2 → 9 → 2 → 0`. Its length is **52.839 km**.

| Solution | Length | Gap to global optimum |
|---|---|---|
| Global optimum (brute force over all 9! = 362 880 routes) | 40.303 km | – |
| Pipeline, every sub-problem solved classically | 52.839 km | +31.1 % |
| Pipeline, every sub-problem solved with QAOA | 52.839 km | +31.1 % |

**Main finding:** QAOA found the optimum of **every** sub-problem, so QAOA itself adds no loss. The whole 31 % gap comes from the *decomposition*: each cluster is a closed loop that has to return to its representative. See [Section 8](#8-interpreting-the-results).

The full notebook runs in about 10 seconds on a laptop.

---

## 2. Files

| File | Purpose |
|---|---|
| `tsp_clustering.ipynb` | The clustering pipeline described here |
| `tsp_library.ipynb` | Shared library: data loading, encoding, QUBO/Hamiltonian, QAOA training and sampling, analysis, plotting |
| `tallinn_osrm_matrix.json` | Input data: 11 points (10 locations + a copy of the depot) and real road distances (metres) and durations (seconds) from OpenStreetMap/OSRM |
| `Tallinn TSP Travel-Time and Distance Matrices.md` | Description of the input data |
| `README.md` | The hackathon problem statement |

### Locations

| Id | Location |
|---|---|
| 0 | Omniva Pallasti (depot, S0) |
| 1 | Kadriorg President's Office |
| 2 | Shaurma Kebab Punane |
| 3 | Kultuurikatel |
| 4 | Patarei Prison |
| 5 | 180 Degrees |
| 6 | TalTech |
| 7 | Tallinn Zoo |
| 8 | Nõmme Spordikeskus |
| 9 | Tallinn Airport |

Point 10 in the data file is the depot again (the "return to depot" point). It is not used, because returning to the depot is already part of every route.

---

## 3. Setup and running

### Requirements

Tested with Python 3.13.2 and:

| Package | Version |
|---|---|
| qiskit | 2.6.1 |
| qiskit-addon-opt-mapper | 0.1.0 |
| qiskit-ibm-runtime | 0.51.0 |
| qiskit-aer | 0.18.2 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| numpy | 2.4.6 |
| matplotlib | 3.11.2 |

```bash
pip install qiskit qiskit-addon-opt-mapper qiskit-ibm-runtime qiskit-aer scikit-learn scipy numpy matplotlib
```

### Running

1. Keep `tsp_clustering.ipynb`, `tsp_library.ipynb` and `tallinn_osrm_matrix.json` in the same folder.
2. Open `tsp_clustering.ipynb` and run all cells (*Restart Kernel → Run All*).

No IBM account or internet connection is needed. Everything runs on local simulators.

---

## 4. The pipeline

```
                 ┌──────── loop in cluster A ────────┐
                 ▼                                   │
  S0 ───────► rep A ──► a1 ──► a2 ──► … ──────────► rep A ───► rep B ──► (loop in B) ──► rep B ───► … ───► S0
  └──────────────────────── central route: S0 → rep A → rep B → rep C → S0 ────────────────────────────────┘
```

1. **Clustering.** All customers except the depot are grouped into `N_CLUSTERS` clusters with KMeans. The depot is excluded because the route starts and ends there.
2. **Representatives.** From each cluster, the location **closest to the depot** (shortest drive depot → location) is chosen as the cluster's representative.
3. **Central graph.** The depot and the representatives form a small TSP. Its optimal route fixes the **order** in which the clusters are visited.
4. **Cluster graphs.** Each cluster is a separate TSP in which the representative plays the role of the depot. The vehicle drives a **closed loop**: it arrives at the representative, visits every location of the cluster and returns to the representative.
5. **Final route.** Each cluster loop is inserted into the central route at its representative. A representative therefore appears twice in the final route: the vehicle arrives there, drives the loop and passes through it again on the way to the next cluster.

### Why clustering?

The position encoding used for TSP needs (n − 1)² qubits for n locations (including the depot):

| Problem | Locations | Qubits |
|---|---|---|
| All 10 locations at once | 10 | 81 |
| Central graph (depot + 3 representatives) | 4 | 9 |
| Largest cluster (4 locations) | 4 | 9 |

Exact statevector simulation is practical up to about 25 qubits. On real hardware, circuits beyond roughly 1 000–2 000 two-qubit gates return mostly noise. Splitting the problem keeps every sub-problem small.

### Why asymmetric distances?

Distances are real driving distances, which differ by direction because of one-way streets and turn restrictions. In the first 5 locations, for example, i → j and j → i differ by up to 0.74 km. A route and its reverse therefore have different lengths, and the notebook keeps the direction everywhere (`SYMMETRIC = False`). The only exception is clustering, which uses the symmetrised matrix (d + dᵀ)/2, because "how close two places are" has no direction.

---

## 5. How one sub-problem is solved with QAOA

Every sub-problem (the central graph and each cluster) goes through the same function, `solve_subproblem(nodes)`. Its first node is the local depot.

### 5.1 Encoding: customer × position

With a fixed local depot and m = n − 1 customers, the binary variable `x_i_p = 1` means "customer i is visited at position p". This gives m² variables, one qubit each.

A bitstring is a valid route when the m × m table of customers × positions has **exactly one 1 in every row and every column**:

```
                position: 0 1 2
customer 3:               1 0 0      route: rep → 3 → 4 → 5 → rep
customer 4:               0 1 0
customer 5:               0 0 1
```

### 5.2 Cost function

| Term | Meaning | Variables | Becomes |
|---|---|---|---|
| `d[depot][i] · x_i_0` | drive depot → first customer | 1 | Z term |
| `d[i][depot] · x_i_last` | drive last customer → depot | 1 | Z term |
| `d[i][j] · x_i_p · x_j_(p+1)` | drive i → j between consecutive positions | 2 | ZZ term |

The **direction** of a drive is encoded by the positions: i is at position p and j at position p + 1. The drives i → j and j → i involve different pairs of variables, so they keep their different asymmetric weights.

### 5.3 Constraints → penalties

- Each customer is visited exactly once: Σ_p x_i_p = 1.
- Each position holds exactly one customer: Σ_i x_i_p = 1.

`OptimizationProblemToQubo` turns each constraint into a penalty `penalty · (Σ x − 1)²`. The square creates further ZZ terms between qubits in the same row or column of the table.

### 5.4 Ising Hamiltonian

Substituting x = (1 − Z)/2 gives a Hamiltonian made of **Z and ZZ terms only**. For a 9-qubit sub-problem there are 39 terms: 9 Z terms, 12 ZZ terms for drives between customers and 18 ZZ terms for penalties.

Because Z and Z⊗Z are diagonal matrices, the Hamiltonian is **diagonal**. Every bitstring is an eigenstate, and the diagonal entries are the energies of all 2ⁿ bitstrings. For a valid route, the energy equals the route length.

### 5.5 Automatic penalty check

`solve_subproblem` starts with `penalty = 20`. It checks that the **lowest-energy bitstring of the Hamiltonian is the classical optimum**, by reading the diagonal and decoding its minimum. If it is not, the penalty is raised ×1.5 and the check repeats. This guards against a penalty too weak to stop invalid bitstrings from becoming the ground state, which can happen for sub-problems with long distances.

### 5.6 Training on the Estimator

`train_with_estimator` minimises the exact energy ⟨H⟩ (`StatevectorEstimator`, no noise) in two stages, the same as in `problem_4.ipynb`:

1. **Linear ramp** (Trotterised quantum annealing): the angles start as a ramp, β from −Δβ towards 0 and γ from 0 towards Δγ. Nelder–Mead tunes only the two strengths Δβ and Δγ.
2. **COBYLA** refines all 2p angles, starting from the tuned ramp.

### 5.7 Sampling and choosing the route

`run_sampler` runs the trained circuit with measurements (`StatevectorSampler`, 10 000 shots). `evaluate_counts` decodes every measured bitstring into a route, or marks it invalid. The sub-problem's answer is the **shortest valid route among all samples** (`best_sampled`). This is how QAOA results are used in practice. The most probable route alone is a poor choice, because QAOA spreads probability over valid routes almost evenly.

### 5.8 Special cases

| Case | What happens |
|---|---|
| Cluster with 1 location | Route is the location itself, length 0, no QAOA |
| Sub-problem with 2 locations | Only one possible route (rep → a → rep), no QAOA |
| No valid route among the samples | The classical optimum is used, so the pipeline can continue. This is reported as `method = "classical fallback"` |
| Cluster larger than `MAX_QUBITS` | The notebook stops with an error and suggests more clusters |

---

## 6. Notebook walkthrough

| Section | Main code | What it does |
|---|---|---|
| **0. Load the library** | loader loop | Executes the code cells of `tsp_library.ipynb` up to the heading `# Implementing the first approach` (or `## 9. example`), so only the library is loaded and its own experiments are not re-run. |
| **1. Configuration** | constants, `load_instance` | Sets the parameters, loads all 10 locations with asymmetric distances and plots the network. |
| **2. Clustering** | `cluster_customers`, `representative`, `plot_clusters` | KMeans on the rows of the symmetrised distance matrix (each customer is described by its distances to all locations). Picks the representative closest to the depot and checks the sub-problem sizes. |
| **3. Solving one sub-problem** | `SubResult`, `ground_state_is_optimal`, `solve_subproblem`, `report` | Everything described in [Section 5](#5-how-one-sub-problem-is-solved-with-qaoa). |
| **4. Central graph** | `solve_subproblem([DEPOT] + reps)` | Solves the TSP on the depot and the representatives. `central.route[1:-1]` gives the cluster order. |
| **5. Cluster graphs** | loop over `cluster_order` | Puts the representative first (it becomes the local depot) and solves each cluster loop. |
| **6. Final route** | `assemble`, `length_of`, `plot_final_route` | Inserts the loops into the central route. An `assert` checks that the length computed edge by edge equals the sum of the parts. The map shows the direction of travel: dashed black for the central route, coloured for cluster loops. |
| **7. Comparison** | `brute_force` | Compares the pipeline with the global optimum and with the same pipeline solved classically. |

### Renumbering of locations

`load_instance(..., nodes=[...])` renumbers the selected locations to 0 … k − 1, so `nodes[0]` becomes the local depot 0. For the central graph `nodes = [0, 1, 6, 2]`, the local indices 0, 1, 2, 3 stand for locations 0, 1, 6, 2. Inside `solve_subproblem`, `to_ids` converts local routes back to original location ids, so every route outside that function uses the original numbering.

---

## 7. Configuration

All parameters are in the cell **1. Configuration**:

| Parameter | Default | Meaning |
|---|---|---|
| `DATA` | `"tallinn_osrm_matrix.json"` | Input data |
| `N_NODES` | `10` | Use locations 0 … N_NODES − 1 |
| `N_CLUSTERS` | `3` | Number of clusters for KMeans |
| `SYMMETRIC` | `False` | `True` mirrors the upper triangle of the distance matrix (same distance in both directions) |
| `PENALTY` | `20` | Starting penalty in km. It is raised automatically when needed. |
| `SHOTS` | `10 000` | Shots per Sampler run |
| `SEED` | `42` | Seed for KMeans and the Sampler (reproducible results) |
| `MAX_QUBITS` | `16` | Largest sub-problem allowed (5 locations) |
| `REPS` | from the library (`2`) | Number of QAOA layers p, defined in `tsp_library.ipynb` |

Effect of `N_CLUSTERS` on the 9 customers:

| `N_CLUSTERS` | Clusters | Representatives | Largest sub-problem |
|---|---|---|---|
| 2 | {1, 2, 3, 4, 5, 9}, {6, 7, 8} | 1, 6 | 6 locations = 25 qubits → too large, stops with an error |
| **3** | {1, 3, 4, 5}, {6, 7, 8}, {2, 9} | 1, 6, 2 | 4 locations = 9 qubits |
| 4 | {1}, {6, 7, 8}, {3, 4, 5}, {2, 9} | 1, 6, 3, 2 | central graph with 5 locations = 16 qubits |

---

## 8. Interpreting the results

### QAOA quality per sub-problem

| Sub-problem | Qubits | Shots on valid routes | Shots on optimal routes |
|---|---|---|---|
| Central graph | 9 | 15.1 % | 2.3 % |
| Cluster of 1 | 9 | 31.6 % | 5.2 % |
| Cluster of 6 | 4 | 94.2 % | 47.4 % |

Even when only a few percent of the shots hit the optimum, 10 000 shots contain it many times, so the best sampled route is optimal in every sub-problem. Larger sub-problems give lower shares. With 9 qubits, most of the probability still goes to invalid bitstrings, because the penalty terms dominate the Hamiltonian.

### Where the 31 % gap comes from

The global optimum is `0 → 1 → 3 → 4 → 5 → 7 → 8 → 6 → 9 → 2 → 0` (40.303 km). It visits the clusters **in the same order** as the pipeline ({1, 3, 4, 5}, then {6, 7, 8}, then {2, 9}). The clustering and the cluster order are therefore good.

The difference is in how the clusters are connected:

- The pipeline's closed loops drive **back to the representative**: 5 → 1, 7 → 6 and 9 → 2. These drives are wasted.
- The optimum instead leaves each cluster **from its last location straight to the next cluster** (5 → 7, 6 → 9).

QAOA loses nothing: the pipeline with classical sub-problems has exactly the same length.

---

## 9. Limitations and next steps

| Limitation | Possible improvement |
|---|---|
| Closed loops return to the representative (main source of the 31 % gap) | **Open paths:** enter a cluster at its representative and leave from the last visited location. This needs a new encoding: a path with a fixed start and a free end. |
| The representative is fixed as the location closest to the depot | Choose entry and exit locations per cluster based on the neighbouring clusters in the central route. |
| QAOA puts most probability on invalid bitstrings | XY mixer with a valid starting route (the circuit never leaves valid routes, so no penalties are needed). Alternatively, a CVaR objective or more layers. |
| All runs use the ideal simulator | A noisy run is possible with `EstimatorV2` / `SamplerV2` in `mode=FakeMarrakesh()` and a matching pass manager (see the noisy example in `tsp_library.ipynb`). For 16 qubits, the transpiled circuit has 850+ two-qubit gates, and noise then dominates the result. |
| KMeans depends on the seed and on the feature choice | Compare several seeds, or cluster on coordinates instead of distance rows. |
| One vehicle only | Step 2 of the hackathon (two vehicles) can reuse the same decomposition, with one vehicle per group of clusters. |
