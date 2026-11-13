# Hackathon problem statement: next-day parcel delivery planning in Estonia

## Context

All parcels for Estonia pass through one central sorting facility. Each day, it receives the previous day's domestic shipments and all incoming international shipments. Every parcel must then be sorted, loaded into a van and delivered somewhere in the country.

To keep the scope manageable, we look only at Estonia.

## The daily planning problem

Every evening, we plan the next day's operation. A typical day has about 50,000 parcels to deliver across the country. The plan must decide:

- **Fleet size:** how many vehicles we need.
- **Staffing:** how many drivers and how many shifts we need.
- **Routing:** which parcels go in which vehicle, and in what order they are delivered.
- **Duration:** how long each route takes, and how long the whole operation takes.
- **Pickups:** many business clients need parcels collected, either on a fixed daily schedule or on demand. These pickups should be added to delivery routes, not served by extra vehicles.

### Objectives

1. Drive as few kilometres as possible in total.
2. Use as few vehicles and drivers as possible.
3. Fit pickups into delivery routes instead of sending separate trips.

### Constraints

- Vehicle capacity, both weight and volume.
- Shift length and working hours.
- Delivery and pickup time windows, where they apply.

## The sorting facility

Sorting happens before delivery, and it affects how well the delivery plan works in practice.

1. Each parcel goes onto a sorting belt, where it is automatically scanned, weighed and measured.
2. It then drops into one of about 500 chutes. This number is illustrative.
3. The contents of each chute are loaded into vehicles.

We choose the rule that sends a parcel to a chute. The rule can use location, route, size, weight or any other property.

**Open question:** how should parcels be assigned to chutes so that the chutes match the vehicle routes? Ideally, one chute or a group of chutes maps to one vehicle or route. This makes loading fast and keeps the vans well packed.

## Out of scope for now

- Customer notifications and delivery time-slot communication, such as "When will you be home?".
- The other Baltic countries.

## The scaled-down toy problem

To simulate the circuits and optimise them on our own machines, we scale the problem down and solve it in three steps.

In every step, the cost to minimise is the total road distance, not the travel time. The distances come from `tallinn_osrm_matrix.json`.

Real road distances depend on direction because of one-way streets and turns: A→B and B→A can differ by up to 1.6 km. Keeping both directions would need about twice as many qubits, which puts even small problems beyond what we can simulate and run. We therefore use one distance per pair of locations, taken from the upper half of the matrix: the distance from the lower-numbered point to the higher-numbered one.

1. **One vehicle, one route.** Solve the travelling salesperson problem (TSP) on 5 or more locations. Find the largest number of locations we can handle. Make sure every team member understands how the solution works.
2. **Two vehicles.** Add a second vehicle and minimise the total distance of both routes. Every parcel must be delivered within one working day. A vehicle spends that day driving and handing over parcels, so the distance it can cover is limited. As a stand-in for this, no vehicle may drive more than 75 % of the shortest one-vehicle tour through the same locations. Without this limit, the best plan leaves the second vehicle at the depot.
3. **Time windows.** Require some locations to be visited within a given time window. A first idea: give each edge a travel time as well as a distance, and require that the travel times along a route stay below a limit.
