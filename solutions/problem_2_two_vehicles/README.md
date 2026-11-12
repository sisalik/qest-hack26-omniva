# Toy problem 2: two vehicles

Our solutions to the two-van problem from the repository [README](../../README.md). The measures and the rules for the leaderboard are defined in the [solutions index](../README.md).

## The task

- **Instance:** the first n points of [`tallinn_osrm_matrix.json`](../../tallinn_osrm_matrix.json). Point 0 is the depot.
- **A plan** is a pair of routes. Each route starts and ends at the depot. Every stop is on exactly one route. A van may stay at the depot.
- **Cost:** the total road distance of both routes, with symmetric distances.
- **Distance limit:** no van may drive more than 75 % of the shortest one-van tour through the same locations. The limit is rounded down to whole metres. For 10 locations it is 30.153 km.
- **A plan is valid** when every stop is visited once and both routes are within the limit.

### Why the limit is part of the task

The repository README asks for two vans and the smallest total distance. Without a further rule the best plan is the problem 1 tour: one van drives everything (40.205 km for 10 locations) and the other stays at the depot. The best plan that uses both vans is longer (42.344 km).

The README says why a second van is needed: one van cannot cover enough ground. The limit states that as a rule. It stands for the working day. Every parcel must be delivered the same day, and a van spends that day driving and handing over parcels, so the distance it can cover is limited. The real rule would limit time: driving time plus a handover time for each stop. The golden circuit handles that rule in the same way, with seconds in place of metres.

How the limit changes the answer for 10 locations:

| Limit, share of the one-van tour | Limit (km) | Shortest plan (km) | Its two routes (km) |
|---|---|---|---|
| 100 % | 40.205 | 40.205 | 40.205 and 0 |
| 90 % | 36.184 | 42.344 | 32.235 and 10.109 |
| 80 % | 32.164 | 44.763 | 30.275 and 14.488 |
| **75 %** | **30.153** | **48.325** | **25.915 and 22.410** |
| 65 % | 26.133 | 48.325 | 25.915 and 22.410 |
| 60 % | 24.123 | No plan exists | |

## Leaderboard

### 10 locations, symmetric distances, limit 30.153 km per van

| Rank | Solution | Qubits | Layers | P(opt) | P(valid) | Mean gap | Cost evaluations for 99 % | Training cost on hardware | Runs today | Version | Evaluated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Golden QAOA](golden_quantum_two_vehicles.ipynb), soft limit, linear ramp | 138 | 40 | 11.5 % | 94.1 % | 1.5 % | 1,558 | 16 circuits | No, simulated | Not committed | 2026-11-12 21:07 |
| 2 | [Golden QAOA](golden_quantum_two_vehicles.ipynb), hard limit, one mixer angle per move | 175 | 10 | 79.4 % | 99.9 % | 1.8 % | 2,733 | 2,327,283 circuits | No, simulated | Not committed | 2026-11-12 21:07 |
| 3 | Grover adaptive search (reference, computed in the golden notebook) | | | | 100 % | | 4,241 | None | No, simulated | Not committed | 2026-11-12 21:07 |
| 4 | [Golden QAOA](golden_quantum_two_vehicles.ipynb), hard limit, one mixer angle per layer | 175 | 20 | 50.2 % | 99.9 % | 2.4 % | 12,607 | 50,868 circuits | No, simulated | Not committed | 2026-11-12 21:07 |
| 5 | [Golden QAOA](golden_quantum_two_vehicles.ipynb), hard limit, linear ramp | 175 | 20 | 24.7 % | 99.9 % | 4.1 % | 30,617 | 25 circuits | No, simulated | Not committed | 2026-11-12 21:07 |
| 6 | Random plan (reference) | | | 0.00022 % | 0.15 % | 13.8 % | 2,088,903 | None | Yes | Not committed | 2026-11-12 21:07 |
| 7 | Brute force: every plan (section 3 of the golden notebook) | | | 100 % | 100 % | 0 % | 3,628,800 | None | Yes, seconds on a laptop | Not committed | 2026-11-12 21:07 |

The hard-limit circuit with one mixer angle per move and 20 layers has the highest P(opt), 97.0 %. It needs 3,602 cost evaluations, so the 10-layer circuit ranks above it.

**Cost evaluations in one shot.** One cost evaluation means working out the two route lengths of a plan once.

- Soft limit: layers + 1.
- Hard limit: 20 + 89 × layers + 1. The 20 are the rounds of amplitude amplification in the start state. The 89 are one cost phase and two limit checks for each of the 44 mixer moves.

Read the rankings with care:

- **Every quantum entry is simulated.** The hard-limit circuit needs 175 qubits and about 143 million two-qubit gates at 20 layers. The soft-limit circuit needs 138 qubits and about 3.8 million at 40 layers. Both are far beyond today's devices.
- **The ranking and P(opt) disagree.** The hard-limit circuit returns the shortest plan in up to 97 % of shots. The soft-limit circuit returns it in 11.5 % of shots, but each of its shots needs about 44 times fewer cost evaluations, so it ranks first.
- **Cost evaluations exclude training.** The hard-limit entries with trained angles would need between 50,000 and 2.3 million circuits to train on hardware. The ramp entries need 16 to 25.
- **The soft limit depends on a penalty.** The penalty must be larger than the most that breaking the limit can save, which is 8.1 km here. A wrong value makes the circuit prefer a plan that breaks the limit.
- **Brute force wins in practice at these sizes.** It is exact and takes seconds.

## Reference values

The exact answers for each instance size, from section 10 of the golden notebook. Each instance has its own limit: 75 % of its shortest one-van tour. "Plans" counts every order of the stops and one depot copy, so the same pair of routes appears up to 8 times. The last column is the hard-limit circuit with a 20-layer linear ramp, reused unchanged on every size.

| Locations | Limit (km) | Shortest plan (km) | Routes | Plans | Plans within the limit | Shortest plans | P(opt), random plan | P(opt), golden hard-limit ramp |
|---|---|---|---|---|---|---|---|---|
| 5 | 12.737 | 17.956 | 0 → 1 → 3 → 4 → 0 and 0 → 2 → 0 | 120 | 16 | 8 | 6.7 % | 68.0 % |
| 6 | 13.733 | 21.703 | 0 → 1 → 2 → 0 and 0 → 3 → 4 → 5 → 0 | 720 | 32 | 16 | 2.2 % | 66.5 % |
| 7 | 22.593 | 36.961 | 0 → 2 → 1 → 3 → 4 → 5 → 0 and 0 → 6 → 0 | 5,040 | 160 | 16 | 0.32 % | 52.4 % |
| 8 | 25.080 | 41.065 | 0 → 2 → 1 → 3 → 4 → 5 → 0 and 0 → 6 → 7 → 0 | 40,320 | 224 | 32 | 0.079 % | 66.8 % |
| 9 | 27.451 | 44.226 | 0 → 2 → 1 → 3 → 4 → 5 → 0 and 0 → 6 → 8 → 7 → 0 | 362,880 | 640 | 32 | 0.0088 % | 86.1 % |
| 10 | 30.153 | 48.325 | 0 → 1 → 3 → 4 → 5 → 9 → 2 → 0 and 0 → 6 → 8 → 7 → 0 | 3,628,800 | 5,576 | 8 | 0.00022 % | 24.7 % |

The instances with 5 to 9 locations have more than one shortest pair of routes. The table shows one of them.

## Summaries

### Golden QAOA: [`golden_quantum_two_vehicles.ipynb`](golden_quantum_two_vehicles.ipynb)

The reference quantum solution. It solves all 10 locations and builds on the one-van golden notebook.

- **Two routes as one order:** a copy of the depot is added to the list of stops. The stops before the copy are the first van's route, the stops after it the second van's. The one-van circuit then works unchanged: one qubit per "item v is visited at step t", 100 position qubits.
- **Mixer:** reverses a stretch of the order. Inside one route this is the 2-opt move. Across the depot copy it moves stops between the vans.
- **Hard limit:** the circuit never leaves the plans within the limit. The start state comes from 20 rounds of amplitude amplification. Each mixer move checks the limit for the plan and for its reversed partner, and acts only when both pass. Up to 97.0 % of shots are the shortest plan and 99.9 % are valid.
- **Soft limit:** the same circuit without the checks in the mixer. Plans over the limit get a penalty in the cost. With a 40-layer ramp, 11.5 % of shots are the shortest plan and 94.1 % are valid.
- **The limit check is a real circuit:** registers add up both route lengths in metres in the Fourier basis and compare them with the limit. It is tested at full size on single plans: 137 qubits for the check and 175 qubits for a limit-checked mixer move.
- **Simulation:** exact, with one amplitude per plan within the limit (5,576) instead of 2¹⁷⁵ amplitudes. A real Qiskit circuit confirms the simulator on 4 locations, with a lookup table in place of the limit check.
- **Angles:** three levels of tuning for the hard limit, from a two-number linear ramp to one angle per mixer gate. The soft limit only has the ramp. The angles are saved in `golden_quantum_two_vehicles_angles.npz`.
- **Main finding:** the second van costs almost nothing. The distance limit is the expensive part, because the circuit has to work it out with arithmetic. Keeping the limit exact gives the best shots but costs about 75 times more gates per shot than a penalty.
- **Not done:** the real one-way road distances, and a simulation of the full 175-qubit circuit in one piece.

## Scoring a solution

Decode every shot to a pair of routes: two tuples of stops, one per van, in driving order. An empty tuple is a van that stays at the depot. Count shots that cannot be decoded under the key `None`. Score the shots with `score_plans` from section 12 of the golden notebook. It marks a shot as valid when every stop appears once and both routes are within the limit.

For smaller instances, pass the number of locations: `score_plans(counts, n=5)`. The reference values above give the answers to expect.
