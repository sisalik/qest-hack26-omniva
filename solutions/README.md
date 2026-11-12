# Solutions to toy problem 1: one vehicle, one route

This directory collects our solutions to the travelling salesperson problem (TSP) from the repository [README](../README.md), so that we can compare them on the same measures.

## The task

- **Instance:** the first n points of [`tallinn_osrm_matrix.json`](../tallinn_osrm_matrix.json). Point 0 is the depot, where the tour starts and ends.
- **Cost:** total road distance. Each pair of locations has one distance, taken from the upper half of the matrix.
- **A tour** is the order in which locations 1 to n − 1 are visited. There are (n − 1)! tours.

## Leaderboard

Solutions are ranked first by the number of locations solved, then by the fewest cost evaluations for a 99 % chance of finding a shortest tour. The measures are defined below.

| Rank | Solution | Kind | Locations | Qubits | Layers | P(opt) | P(valid) | Mean gap | Cost evaluations for 99 % | Training cost on hardware | Runs today |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Golden QAOA](golden_quantum_tsp.ipynb), one mixer angle per move | Quantum, simulated | 10 | 82 | 20 | 98.8 % | 100 % | 0.5 % | 42 | 3,765,333 circuits | No |
| 2 | [Golden QAOA](golden_quantum_tsp.ipynb), one mixer angle per layer | Quantum, simulated | 10 | 82 | 40 | 79.8 % | 100 % | 1.0 % | 123 | 102,396 circuits | No |
| 3 | [Golden QAOA](golden_quantum_tsp.ipynb), linear ramp | Quantum, simulated | 10 | 82 | 80 | 90.9 % | 100 % | 1.5 % | 162 | 24 circuits | No |
| 4 | Grover adaptive search (reference, computed in the golden notebook) | Quantum, simulated | 10 | | | | 100 % | | 2,947 | None | No |
| 5 | [Brute force](brute_force_tsp.ipynb) | Classical, exact | 10 | | | 100 % | 100 % | 0 % | 362,880 | None | Yes, 0.2 s on a laptop |
| 6 | Random guessing (reference) | Classical | 10 | | | 0.00055 % | 100 % | 80.8 % | 835,560 | None | Yes |

Read the ranking with care:

- **The quantum entries are simulated.** The golden circuit needs 82 qubits and about 191,000 two-qubit gates at 20 layers. That is far beyond today's devices.
- **Cost evaluations exclude training.** The top entry would need about 3.8 million circuits to train on hardware, more than checking every tour. It shows what the circuit can express, not a practical way to find the answer.
- **Brute force wins in practice at this size.** It is exact and takes a fraction of a second. Its cost grows as (n − 1)!, so it stops being usable near 15 locations.

## Measures

Use these for every solution. `score_tours` in section 13 of the golden notebook computes the first four from a dictionary of shots.

1. **P(opt):** the share of shots that return a shortest tour.
2. **P(valid):** the share of shots that are valid tours.
3. **Mean gap:** how much longer the average sampled valid tour is than the shortest one.
4. **Cost evaluations for 99 %:** the shots needed for a 99 % chance of seeing a shortest tour at least once, multiplied by (layers + 1). A classical method counts one evaluation per tour it checks.
5. **Circuit cost:** qubits, layers and two-qubit gates after transpilation, and the circuits needed for training.

Also say whether the solution runs on today's hardware or only in simulation.

## Reference values

The shortest tours for each instance size come from the brute-force notebook. Some small instances have more than one shortest loop, because several points lie along the same road. The last column is the golden circuit with a 20-layer linear ramp, reused unchanged on every size.

| Locations | Tours | Shortest tour (km) | Shortest tours | One shortest tour | P(opt), random | P(opt), golden ramp |
|---|---|---|---|---|---|---|
| 5 | 24 | 16.983 | 4 | 0 → 2 → 1 → 3 → 4 → 0 | 16.7 % | 87.6 % |
| 6 | 120 | 18.311 | 8 | 0 → 2 → 1 → 3 → 4 → 5 → 0 | 6.7 % | 87.5 % |
| 7 | 720 | 30.124 | 2 | 0 → 1 → 3 → 4 → 5 → 6 → 2 → 0 | 0.3 % | 61.8 % |
| 8 | 5,040 | 33.441 | 2 | 0 → 1 → 3 → 4 → 5 → 7 → 6 → 2 → 0 | 0.04 % | 35.3 % |
| 9 | 40,320 | 36.602 | 2 | 0 → 1 → 3 → 4 → 5 → 7 → 8 → 6 → 2 → 0 | 0.005 % | 19.1 % |
| 10 | 362,880 | 40.205 | 2 | 0 → 1 → 3 → 4 → 5 → 7 → 8 → 6 → 9 → 2 → 0 | 0.00055 % | 17.9 % |

On the real one-way roads the shortest 10-location route is 40.303 km, along the same loop.

## Summaries

### Golden QAOA: [`golden_quantum_tsp.ipynb`](golden_quantum_tsp.ipynb)

The reference quantum solution. It solves all 10 locations.

- **Encoding:** one qubit per "stop v is visited at step t", 81 qubits plus one helper.
- **No invalid answers:** the circuit starts in an equal superposition of all valid tours, and the mixer only moves amplitude between valid tours. There are no penalty terms and every shot is a valid tour.
- **Mixer:** reverses a stretch of the route, which is the classical 2-opt move. At 20 layers it reaches 17.9 % P(opt), against 3.5 % for swap mixers and 0.9 % for Grover search.
- **Simulation:** exact, with one amplitude per valid tour (362,880) instead of 2⁸² amplitudes. A real Qiskit gate-level circuit confirms the simulator on 4 and 5 locations.
- **Angles:** three levels of tuning, from a two-number linear ramp to one angle per mixer gate. The trained angles are saved in `golden_quantum_tsp_angles.npz`.
- **Also solves** the real one-way road distances: 99.5 % P(opt) at 20 layers.

### Brute force: [`brute_force_tsp.ipynb`](brute_force_tsp.ipynb)

The exact classical baseline. It checks every tour and keeps the shortest, for 5 to 10 locations, on both the symmetric and the one-way distances. Use its table as the ground truth when scoring another solution.

## Running the notebooks

Both notebooks run in the `../qest-hack26` environment and find the matrix file in the repository root.

```bash
cd solutions
uv run --project ~/dev/qest-hack26 jupyter nbconvert --to notebook --execute golden_quantum_tsp.ipynb --inplace --ExecutePreprocessor.timeout=-1
```

The golden notebook takes about 2 minutes with the saved angles. Retraining (`RETRAIN = True`) takes about 1.5 hours and needs `numba`: add `--with numba` after `--project ~/dev/qest-hack26`.

## Adding a solution

1. Put the notebook in this directory.
2. Decode every shot to a tour and score the shots with `score_tours` from the golden notebook. Count shots that are not valid tours under the key `None`.
3. Add a row to the leaderboard and a short summary below it.
