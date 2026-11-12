# Tallinn TSP: Travel-Time and Distance Matrices

Nov 12, 2026 · @Deniss Kross

## Overview

We turned 10 real Tallinn locations, plus a return to the depot, into two 11 × 11 matrices of real road travel: one of driving times in seconds, one of driving distances in metres. These matrices are the cost input for our travelling salesman problem (TSP). Every cell is the cost of driving from one point to another, so a tour's cost is the sum of the cells it passes through.

The matrices come from OpenStreetMap road data for Estonia. Unlike straight-line distances, they follow the actual road network, including one-way streets and turn restrictions.

## The 10 points

Point 0 is the depot, where the tour starts. Point 10 is the same office again, where the tour must end. The index is the row and column number used in both matrices.

| Index | Place | Latitude | Longitude |
| --- | --- | --- | --- |
| 0 | Omniva, Pallasti 28 (depot) | 59.430219 | 24.792326 |
| 1 | Office of the President, Kadriorg | 59.437975 | 24.793941 |
| 2 | Shaurma Kebab Punane, Lasnamäe | 59.433546 | 24.827319 |
| 3 | Kultuurikatel (Creative Hub) | 59.444289 | 24.751277 |
| 4 | Patarei Sea Fortress | 59.450718 | 24.742094 |
| 5 | 180 Degrees Restaurant, Noblessner | 59.452054 | 24.728923 |
| 6 | TalTech campus | 59.394973 | 24.671848 |
| 7 | Tallinn Zoo | 59.419769 | 24.659820 |
| 8 | Nõmme Spordikeskus | 59.389657 | 24.653064 |
| 9 | Tallinn Airport | 59.414550 | 24.833465 |
| 10 | Omniva, Pallasti 28 (return to depot) | 59.430219 | 24.792326 |

Coordinates come from Google Maps place data.

## What the routing engine generates

You give it a list of points; it returns every point-to-point driving time and distance in one response. The input is an ordered list of coordinates, written longitude first, then latitude. The output keeps that same order for rows and columns.

| Output | Meaning | Unit | Type |
| --- | --- | --- | --- |
| `durations` | Driving time from point i to point j | seconds | integer |
| `distances` | Driving distance from point i to point j | metres | integer |

Both are square matrices with one row and one column per input point. Cell \[i\]\[j\] is the trip from row point i to column point j. Times are free-flow estimates from road types and speed limits, without live traffic.

A minimal example with three points returns this shape:

```json
{"durations": [[0, 493, 881], [447, 0, 998], [944, 805, 0]],
 "distances": [[0, 4866, 8299], [4079, 0, 11129], [8757, 8905, 0]]}
```

## Duration matrix (seconds)

The fastest hop is 180 Degrees to Patarei (133 s); the slowest is Kadriorg to Nõmme (1,283 s, about 21 minutes). Row = from, column = to.

| From \\ To | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **0** | 0 | 375 | 267 | 432 | 567 | 644 | 805 | 922 | 1060 | 454 | 0 |
| **1** | 407 | 0 | 463 | 367 | 502 | 579 | 1029 | 1146 | 1283 | 722 | 407 |
| **2** | 258 | 525 | 0 | 601 | 736 | 813 | 908 | 1026 | 1163 | 291 | 258 |
| **3** | 480 | 410 | 637 | 0 | 165 | 241 | 887 | 923 | 1142 | 742 | 480 |
| **4** | 600 | 531 | 758 | 208 | 0 | 137 | 940 | 966 | 1195 | 863 | 600 |
| **5** | 632 | 562 | 790 | 240 | 133 | 0 | 877 | 902 | 1132 | 895 | 632 |
| **6** | 795 | 1030 | 932 | 915 | 1016 | 958 | 0 | 397 | 321 | 979 | 795 |
| **7** | 887 | 1121 | 1024 | 900 | 1000 | 942 | 350 | 0 | 561 | 1071 | 887 |
| **8** | 1018 | 1252 | 1155 | 1138 | 1239 | 1180 | 313 | 570 | 0 | 1202 | 1018 |
| **9** | 439 | 685 | 306 | 690 | 826 | 902 | 962 | 1080 | 1217 | 0 | 439 |
| **10** | 0 | 375 | 267 | 432 | 567 | 644 | 805 | 922 | 1060 | 454 | 0 |

## Distance matrix (metres)

The shortest hop is 180 Degrees to Patarei (784 m); the longest is the Airport to Nõmme (13,061 m). Row = from, column = to.

| From \\ To | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **0** | 0 | 2676 | 2768 | 3937 | 5136 | 5659 | 9325 | 10133 | 10951 | 4262 | 0 |
| **1** | 2909 | 0 | 4471 | 3221 | 4420 | 4943 | 10508 | 11315 | 12133 | 7169 | 2909 |
| **2** | 2747 | 5207 | 0 | 6134 | 7334 | 7856 | 10924 | 11731 | 12549 | 3079 | 2747 |
| **3** | 4219 | 3479 | 6826 | 0 | 1387 | 1910 | 8621 | 8110 | 10247 | 7257 | 4219 |
| **4** | 5163 | 4423 | 7770 | 1625 | 0 | 805 | 8214 | 8235 | 9840 | 8202 | 5163 |
| **5** | 5436 | 4696 | 8043 | 1897 | 784 | 0 | 8343 | 8364 | 9969 | 8474 | 5436 |
| **6** | 9157 | 10735 | 11000 | 8451 | 9810 | 9320 | 0 | 3296 | 1963 | 11448 | 9157 |
| **7** | 9915 | 11493 | 11758 | 8327 | 9686 | 9196 | 3084 | 0 | 4494 | 12205 | 9915 |
| **8** | 10771 | 12349 | 12614 | 10064 | 11423 | 10933 | 1998 | 4510 | 0 | 13061 | 10771 |
| **9** | 4206 | 5836 | 3163 | 6783 | 7983 | 8505 | 11354 | 12162 | 12980 | 0 | 4206 |
| **10** | 0 | 2676 | 2768 | 3937 | 5136 | 5659 | 9325 | 10133 | 10951 | 4262 | 0 |
