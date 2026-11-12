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

## 50,000 parcels a day, one sorting hub

- Every evening Omniva plans the next day for all of Estonia: **fleet size, drivers, routes**
- Goals: fewest kilometres, fewest vehicles, pickups folded into delivery routes
- Constraints: vehicle capacity, shift length, delivery **time windows**

**Why it is hard:** a route through *n* stops has *(n − 1)!* possible orders.
10 stops → 362,880 routes; 20 stops → 1.2 × 10¹⁷. Adding vehicles and time windows makes it worse.

<!--
~30 s (part of the 1-minute business block).
Classical solvers handle this today with heuristics; the question is what a quantum approach costs.
-->

---

### 1 · Business problem

## How many qubits would the real problem need?

Encoding "stop × position in the route": one qubit per (stop, step) pair.

| Stops *n* | Qubits ≈ *n*² | Two-qubit terms per QAOA layer ≈ *n*³ |
|---|---|---|
| 5 (our toy) | 25 | ~200 |
| 9 (Tallinn data) | 81 | ~1,200 |
| <span class="todo">[stops per real route]</span> | <span class="todo">[…]</span> | <span class="todo">[…]</span> |
| 50,000 (whole day, one route) | 2.5 × 10⁹ | ~2.5 × 10¹⁴ |

**Scaling:** qubits grow **quadratically**, circuit size per layer **cubically**.

<!--
~30 s. Answer the two required questions explicitly:
- full problem: billions of qubits for one big route; even split per vehicle it is far beyond today's hardware;
- scaling: neither linear nor just quadratic; the circuit grows like n^3 because every pair of stops at consecutive steps gets a term.
TODO: fill the row for a realistic single-vehicle route once we fix the numbers.
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
