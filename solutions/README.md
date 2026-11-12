# Solutions to toy problem 1: one vehicle, one route

This directory collects our solutions to the travelling salesperson problem (TSP) from the repository [README](../README.md), so that we can compare them on the same measures.

## The task

- **Instance:** the first n points of [`tallinn_osrm_matrix.json`](../tallinn_osrm_matrix.json). Point 0 is the depot, where the tour starts and ends.
- **Cost:** total road distance. The repository README asks for one distance per pair of locations, taken from the upper half of the matrix ("symmetric distances"). Some solutions use the real one-way distances instead, and the leaderboard says which.
- **A tour** is the order in which locations 1 to n − 1 are visited. There are (n − 1)! tours.

## Leaderboard

There is one table per instance. Larger instances come first. Within a table, solutions are ranked by the fewest cost evaluations for a 99 % chance of finding a shortest tour. The measures are defined below.

**Version** is the commit of the solution's notebook that was scored. **Evaluated** is when the measures were computed (Estonian time). Score a solution again when its notebook changes.

### 10 locations, symmetric distances

| Rank | Solution | Qubits | Layers | P(opt) | P(valid) | Mean gap | Cost evaluations for 99 % | Training cost on hardware | Runs today | Version | Evaluated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Golden QAOA](golden_quantum_tsp.ipynb), one mixer angle per move | 82 | 20 | 98.8 % | 100 % | 0.5 % | 42 | 3,765,333 circuits | No, simulated | `dd61898` | 2026-11-12 19:59 |
| 2 | [Golden QAOA](golden_quantum_tsp.ipynb), one mixer angle per layer | 82 | 40 | 79.8 % | 100 % | 1.0 % | 123 | 102,396 circuits | No, simulated | `dd61898` | 2026-11-12 19:59 |
| 3 | [Golden QAOA](golden_quantum_tsp.ipynb), linear ramp | 82 | 80 | 90.9 % | 100 % | 1.5 % | 162 | 24 circuits | No, simulated | `dd61898` | 2026-11-12 19:59 |
| 4 | Grover adaptive search (reference, computed in the golden notebook) | | | | 100 % | | 2,947 | None | No, simulated | `dd61898` | 2026-11-12 19:59 |
| 5 | [Brute force](brute_force_tsp.ipynb) | | | 100 % | 100 % | 0 % | 362,880 | None | Yes, 0.2 s on a laptop | `dd61898` | 2026-11-12 19:57 |
| 6 | Random valid tour (reference) | | | 0.00055 % | 100 % | 80.8 % | 835,560 | None | Yes | `dd61898` | 2026-11-12 19:59 |

### 5 locations, one-way distances

| Rank | Solution | Qubits | Layers | P(opt) | P(valid) | Mean gap | Cost evaluations for 99 % | Training cost | Runs today | Version | Evaluated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Brute force](brute_force_tsp.ipynb) | | | 100 % | 100 % | 0 % | 24 | None | Yes | `dd61898` | 2026-11-12 19:57 |
| 2 | [Eli's QAOA](../Eli_solution.ipynb) | 16 | 2 | 0.32 % | 7.6 % | 26.2 % | 4,248 | 200 simulated circuits | No, simulated | `93d1c30` | 2026-11-12 20:10 |
| 3 | [Artem's QAOA](../Artem_solution_based_on_Eli_solution_iqm.ipynb), simulated | 16 | 1 | 0.20 % | 5.7 % | 28.5 % | 4,630 | About 14,400 simulated circuits | No, simulated | `ad8f8fc` | 2026-11-12 20:10 |
| 4 | [Artem's QAOA](../Artem_solution_based_on_Eli_solution_iqm.ipynb), on IQM Emerald | 16 | 1 | 0 of 5,000 shots | 0.1 % | Not available | Not reached | As above | Yes, 280 CZ gates on the device | `ad8f8fc` | 2026-11-12 20:10 |
| 5 | Random 16-bit string (reference) | 16 | 0 | 0.0015 % | 0.037 % | 26.5 % | 301,803 | None | Yes | | 2026-11-12 20:10 |

The measures for ranks 2 to 5 are computed in [`penalty_qaoa_scores.ipynb`](penalty_qaoa_scores.ipynb).

Read the rankings with care:

- **Most quantum entries are simulated.** The golden circuit needs 82 qubits and about 191,000 two-qubit gates at 20 layers. That is far beyond today's devices.
- **Cost evaluations exclude training.** The top golden entry would need about 3.8 million circuits to train on hardware, more than checking every tour. It shows what the circuit can express, not a practical way to find the answer.
- **Brute force wins in practice at these sizes.** It is exact and takes a fraction of a second. Its cost grows as (n − 1)!, so it stops being usable near 15 locations.
- **The two tables are different instances.** The 5-location entries use one-way distances and 16 qubits with penalties. For a rough comparison, the golden circuit on 5 locations with symmetric distances reaches 87.6 % P(opt) with 17 qubits and a 20-layer ramp.

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

| Locations | Tours | Shortest tour (km) | Shortest tours | One shortest tour | P(opt), random valid tour | P(opt), golden ramp |
|---|---|---|---|---|---|---|
| 5 | 24 | 16.983 | 4 | 0 → 2 → 1 → 3 → 4 → 0 | 16.7 % | 87.6 % |
| 6 | 120 | 18.311 | 8 | 0 → 2 → 1 → 3 → 4 → 5 → 0 | 6.7 % | 87.5 % |
| 7 | 720 | 30.124 | 2 | 0 → 1 → 3 → 4 → 5 → 6 → 2 → 0 | 0.3 % | 61.8 % |
| 8 | 5,040 | 33.441 | 2 | 0 → 1 → 3 → 4 → 5 → 7 → 6 → 2 → 0 | 0.04 % | 35.3 % |
| 9 | 40,320 | 36.602 | 2 | 0 → 1 → 3 → 4 → 5 → 7 → 8 → 6 → 2 → 0 | 0.005 % | 19.1 % |
| 10 | 362,880 | 40.205 | 2 | 0 → 1 → 3 → 4 → 5 → 7 → 8 → 6 → 9 → 2 → 0 | 0.00055 % | 17.9 % |

On the real one-way roads there is a single shortest route for each size. For 5 locations it is 16.965 km (0 → 3 → 4 → 1 → 2 → 0). For 10 locations it is 40.303 km, along the same loop as the symmetric answer.

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

### Eli's QAOA: [`../Eli_solution.ipynb`](../Eli_solution.ipynb)

Standard QAOA on 5 locations with one-way distances.

- **Encoding:** one qubit per "location i is visited at position p", 16 qubits. A penalty of 100 makes invalid bitstrings expensive.
- **Circuit:** Qiskit's `QAOAAnsatz` with 2 layers, 168 CX gates per layer before routing.
- **Angles:** COBYLA from a fixed start, 200 evaluations of the exact expectation value.
- **Result:** 7.6 % of shots are valid tours and 0.32 % are the shortest tour. That is 200 times better than a random bitstring. The best of 10,000 simulated shots is the shortest tour.
- **Limit:** the mean gap among valid shots (26.2 %) is the same as for random valid tours (26.5 %). The penalty is much larger than the distances, so the circuit finds valid tours but cannot tell short ones from long ones.

### Artem's QAOA on IQM Emerald: [`../Artem_solution_based_on_Eli_solution_iqm.ipynb`](../Artem_solution_based_on_Eli_solution_iqm.ipynb)

Eli's model with 1 layer, run on a real quantum computer.

- **Angles:** a grid search over the two angles that maximises P(valid), then four rounds of zooming in. The shortest valid tour is then picked classically from the shots.
- **Simulated:** 5.7 % valid shots and 0.20 % shortest tours, close to Eli's 2-layer result with half the gates.
- **On hardware:** the circuit needs 280 CZ gates on the 54-qubit IQM Emerald device after routing. Of 5,000 shots, 5 were valid tours and none was the shortest. A random bitstring would give about 2 valid shots, so the result is close to noise. The best sampled tour was 19.831 km, 16.9 % longer than the shortest.
- **This is our only result from real hardware.** It shows the gap between simulation and today's devices at 16 qubits.

## Running the notebooks

The notebooks in this directory run in the `../qest-hack26` environment and find the matrix file in the repository root.

```bash
cd solutions
uv run --project ~/dev/qest-hack26 jupyter nbconvert --to notebook --execute golden_quantum_tsp.ipynb --inplace --ExecutePreprocessor.timeout=-1
```

The golden notebook takes about 2 minutes with the saved angles. Retraining (`RETRAIN = True`) takes about 1.5 hours and needs `numba`: add `--with numba` after `--project ~/dev/qest-hack26`. The other two notebooks take seconds.

## Adding a solution

1. Put the notebook in this directory, or link to it from here.
2. Decode every shot to a tour and score the shots with `score_tours` from the golden notebook. Count shots that are not valid tours under the key `None`. For standard QAOA with penalties, `penalty_qaoa_scores.ipynb` shows how to score a circuit from its angles.
3. Add a row to the leaderboard table for its instance, with the commit of the notebook that was scored and the time of scoring.
4. Add a short summary below.
