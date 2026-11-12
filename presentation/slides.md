---
marp: true
size: 16:9
paginate: true
title: Omniva next-day delivery planning with QAOA
style: |
  section {
    font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
    background: #F7F6F2;
    color: #14213D;
    font-size: 28px;
    padding: 64px 80px;
  }
  h1 { color: #14213D; font-size: 56px; margin-bottom: 16px; }
  h2 { color: #14213D; font-size: 44px; margin-bottom: 24px; }
  h3 { color: #2B6CB0; font-size: 22px; letter-spacing: 2px; text-transform: uppercase; margin: 0 0 8px; }
  strong { color: #B5541C; }
  table { font-size: 24px; }
  th { background: #E9E5DC; }
  .todo { color: #B5541C; font-weight: 600; }
  .small { font-size: 22px; color: #4A5568; }
  section.lead { background: #14213D; color: #F4F1EA; }
  section.lead h1 { color: #F4F1EA; font-size: 72px; }
  section.lead h3 { color: #F2A65A; }
  section.lead .todo { color: #F2A65A; }
  section::after { color: #8A94A6; font-size: 18px; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

### QEst Hack 2026 · Team <span class="todo">[team name]</span>

# Planning next-day parcel delivery with QAOA

<span class="todo">[team members]</span>

<!--
~10 s. Who we are, which problem.
-->

---

### 1 · Business problem

## One day of parcels in Tallinn

<style scoped>
table { font-size: 24px; }
th { font-size: 48px; color: #B5541C; background: transparent; }
td { color: #4A5568; }
table, tr, th, td { border: none !important; background: transparent !important; }
th { white-space: nowrap; }
</style>

| ~17,000 | 94 | 10⁴ – 10⁸ | *n*² → *n*³ |
|---|---|---|---|
| parcels a day | Omniva parcel lockers | qubits for the full problem | qubits grow quadratically, the circuit cubically |

- Every evening: which van takes which parcels, and in what order, within shifts and time windows
- **Why it is hard:** *n* stops have *(n − 1)!* possible routes; 20 stops already give 10¹⁷

<!--
~30 s.
17,000/day: 50,000 parcels a day in Estonia (problem statement) x Tallinn's share of the population (457,000 / 1,360,745). Our estimate, not an Omniva figure.
94 Omniva parcel lockers in Tallinn.
Qubits: encoding "stop x position", n^2 qubits for n stops. Lower bound: one round of the 94 lockers = ~8,800 qubits. Upper bound: every parcel its own stop, 17,000^2 = ~3 x 10^8. Today's hardware: tens to ~150 qubits.
Scaling (required question): qubits grow quadratically; two-qubit terms per QAOA layer grow cubically (~2 n^3), so the circuit grows faster than the qubit count.
Sources and calculations: presentation/README.md.
-->

---

### 1 · Business problem

## Three toy tasks on real Tallinn roads

Data: depot Omniva Pallasti + 9 real Tallinn stops, real road distances and travel times. Cost to minimise: **distance**.

1. **One van, one route.** The shortest round trip through 5+ stops. How many stops can we handle?
2. **Two vans.** Too many stops for one van, even on its best route: split them between two vans, minimise the total distance.
3. **Time windows.** Some stops accept deliveries only in a given window; the route is still the shortest one that is on time.

<!--
~30 s.
Data: tallinn_osrm_matrix.json, OSRM road network, 11 x 11 (depot twice: start and return), distances in metres and times in seconds; one-way streets make the matrices asymmetric.
Classical reference for step 1: brute force on depot + 4 stops = 16.96 km; all 9 stops: 40.3 km, 73 min (VROOM agrees with brute force).
-->

---

### 2 · Results · Step 1

## One vehicle: TSP on <span class="todo">[n]</span> Tallinn stops

<!-- ![w:900](img/step1_results.png) -->

<span class="todo">[graph: probability of the optimal route vs number of layers / vs number of stops]</span>

- Qubits: <span class="todo">[…]</span> · layers: <span class="todo">[…]</span> · P(optimal route): <span class="todo">[…]</span>
- Largest *n* we could handle: <span class="todo">[…]</span>

<!--
~50 s. Real road times and distances from OSRM (Tallinn, 10 points incl. depot).
Say what limited n: simulator memory, circuit depth, or success probability.
-->

---

### 2 · Results · Step 2

## Two vehicles

<!-- ![w:900](img/step2_results.png) -->

<span class="todo">[map or graph of the two routes; total distance vs one vehicle]</span>

- Approach: <span class="todo">[e.g. split the stops between vehicles first, then route each]</span>
- Result: <span class="todo">[…]</span>

<!--
~50 s.
-->

---

### 2 · Results · Step 3

## Time windows

<!-- ![w:900](img/step3_results.png) -->

<span class="todo">[shortest route without windows vs feasible route with windows]</span>

- How windows enter the model: <span class="todo">[…]</span>
- Result: <span class="todo">[…]</span>

<!--
~50 s. The key picture: the shortest route breaks a window, the solver picks a slightly longer one that is on time.
-->

---

### 3 · Lessons learned

## What we learned

- <span class="todo">[lesson 1: e.g. the encoding matters more than the optimizer]</span>
- <span class="todo">[lesson 2: e.g. constraints as penalties vs built into the encoding]</span>
- <span class="todo">[lesson 3: e.g. what changed between simulator and real hardware]</span>

<!--
~1 min.
-->

---

### 4 · Next steps

## Where this could go

- <span class="todo">[e.g. hybrid: classical clustering of 50,000 parcels, quantum for small sub-routes]</span>
- <span class="todo">[e.g. map clusters to sorting chutes]</span>
- <span class="todo">[e.g. vehicle capacity, pickups]</span>

<!--
~30 s. Then Q&A (2 min).
-->
