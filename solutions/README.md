# Solutions to the toy problems

This directory collects our solutions to the scaled-down toy problems from the repository [README](../README.md), so that we can compare them on the same measures.

## Problems

Each problem has its own directory with a leaderboard, the exact answers and a summary of every solution.

| Problem | Task | Documents | Golden quantum solution |
|---|---|---|---|
| 1. One vehicle, one route | Shortest tour from the depot through every stop | [Leaderboard and summaries](problem_1_one_vehicle/README.md) | [`golden_quantum_tsp.ipynb`](problem_1_one_vehicle/golden_quantum_tsp.ipynb) |
| 2. Two vehicles | Shortest pair of routes, with a distance limit per van | [Leaderboard and summaries](problem_2_two_vehicles/README.md) | [`golden_quantum_two_vehicles.ipynb`](problem_2_two_vehicles/golden_quantum_two_vehicles.ipynb) |
| 3. Time windows | Not started | | |

## What all problems share

- **Instance:** the first n points of [`tallinn_osrm_matrix.json`](../tallinn_osrm_matrix.json). Point 0 is the depot, where every route starts and ends.
- **Cost:** total road distance. The repository README asks for one distance per pair of locations, taken from the upper half of the matrix ("symmetric distances"). A leaderboard says so when a solution uses the real one-way distances instead.
- **An answer** is a tour in problem 1 and a pair of routes in problem 2. An answer is **valid** when it obeys every rule of its problem.

## Measures

Use these for every solution.

1. **P(opt):** the share of shots that return a shortest valid answer.
2. **P(valid):** the share of shots that are valid answers.
3. **Mean gap:** how much longer the average valid shot is than the shortest valid answer.
4. **Cost evaluations for 99 %:** the shots needed for a 99 % chance of seeing a shortest answer at least once, multiplied by the cost evaluations in one shot. One cost evaluation means working out the length of one answer. A classical method counts one evaluation per answer it checks. Each problem's README says how many evaluations one shot of a circuit takes.
5. **Circuit cost:** qubits, layers and two-qubit gates after transpilation, and the circuits needed for training.

Also say whether the solution runs on today's hardware or only in simulation.

Each golden notebook has a function that computes the first four measures from a dictionary of shots: `score_tours` for problem 1 and `score_plans` for problem 2.

## Leaderboards

- There is one table per instance. Larger instances come first.
- Within a table, solutions are ranked by the fewest cost evaluations for a 99 % chance of finding a shortest answer.
- **Version** is the commit of the solution's notebook that was scored.
- **Evaluated** is when the measures were computed (Estonian time).
- Score a solution again when its notebook changes.

## Running the notebooks

The notebooks run in the `../qest-hack26` environment and find the matrix file in the repository root. Run them from their own directory, because the golden notebooks load their saved angles from there.

```bash
cd solutions/problem_1_one_vehicle
uv run --project ~/dev/qest-hack26 --with numba jupyter nbconvert --to notebook --execute golden_quantum_tsp.ipynb --inplace --ExecutePreprocessor.timeout=-1
```

| Notebook | With the saved angles | Retraining (`RETRAIN = True`) |
|---|---|---|
| `problem_1_one_vehicle/golden_quantum_tsp.ipynb` | About 2 minutes | About 1.5 hours |
| `problem_2_two_vehicles/golden_quantum_two_vehicles.ipynb` | About 2 minutes | About 10 minutes |
| The other notebooks | Seconds | |

`--with numba` adds the `numba` package, which is not in the environment. The golden notebooks also run without it, but much more slowly.

## Adding a solution

1. Put the notebook in the directory of its problem, or link to it from that directory's README.
2. Decode every shot to an answer and score the shots with the scoring function of that problem's golden notebook. Count shots that cannot be decoded under the key `None`.
3. Add a row to the leaderboard table for its instance, with the commit of the notebook that was scored and the time of scoring.
4. Add a short summary to the same README.
