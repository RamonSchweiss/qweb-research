# QWeb © Research — Calculations, designs and figures

Every figure and every number quoted in the articles at
[qweb-quantum.com](https://qweb-quantum.com) comes from a calculation.
This repository holds those calculations so that anyone can check them.

Two further kinds of document sit beside them. `designs/` holds the
design notes for measurements that have not been run yet, committed
before the first computation so that the date on a hypothesis is a fact
rather than a claim; when something learned afterwards changes one, it
is recorded as a dated addendum and the original text is left standing.
`figures/` holds the scripts that draw the figures in the articles.

Each script is standalone, prints its results, and states which article
and which figure it belongs to. Nothing is hidden in a library.

## Requirements

```
pip install numpy scipy scikit-learn pennylane
```

Two scripts use an optional extra and say so when it is missing rather
than failing: `routed_partition_orbit.py` needs `qiskit`, and the
cross-check at the end of `gate_vs_state_partition.py` needs `memq_dqc`.

```
pip install qiskit
```

Otherwise nothing else. The scripts are deliberately plain: no notebooks,
no plotting dependencies, no framework. They print numbers you can compare
against the articles.

## Running everything

```
python run_all.py          # the quick checks, about five seconds
python run_all.py --all    # including the slow experiments, about twenty-five minutes
```

Two files are not ordinary scripts. `qdnn_variants.py` is a module the QDNN
scripts import. `qdnn_sweep.py` needs a width argument — run it without one
and it explains itself.

## What is here

| Script | Article | What it verifies |
|---|---|---|
| `no_cloning.py` | Two Answers to One Question | The three-line no-cloning proof, checked numerically |
| `chsh_bound.py` | Two Answers to One Question | Classical bound 2, quantum bound 2√2, and where the Bell bound sits on the scale |
| `entanglement_entropy.py` | Where the Research Areas Converge | S(θ) for the standard family, Schmidt rank against entropy |
| `consistency_identity.py` | Where the Research Areas Converge | E + C = 1 for pure states, and the counterexample that breaks it for mixed ones |
| `mixed_states.py` | Where the Research Areas Converge | Wootters' concurrence, the shortfall S − E, and where it peaks |
| `bloch_states.py` | Where the Research Areas Converge | The six Pauli eigenstates, their preparation, and why no gate reaches I/2 |
| `kruskal_partition.py` | Where the Research Areas Converge | Entropy-weighted partitioning, and Borůvka's parallel rounds |
| `coherence_limit.py` | Where the Research Areas Converge | Round trip against coherence time; the 30 km bound |
| `scheduling_limit.py` | Where the Research Areas Converge | Why central scheduling fails before coherence does |
| `node_slices.py` | What a Node Actually Holds | A node holds no reduced state; the trace comes to its own share |
| `qdnn_ablation.py` | The Layer That Nobody Trains | Four variants at matched capacity, pairwise tests, gradient traces |
| `qdnn_replicate.py` | The Layer That Nobody Trains | The same comparison on three datasets: breast cancer, wine, digits |
| `qdnn_sweep.py` | The Layer That Nobody Trains | The capacity sweep: how the cost of freezing falls as classical layers are added |
| `hamiltonian_terms.py` | What a Hamiltonian Actually Says | Hermiticity, the two commutators, and where the ground state gets its entanglement |
| `gate_rabi.py` | How a Gate Is Actually Made | The closed form, the rotating wave approximation, and what detuning costs |
| `partition_information.py` | in progress, joint with V. Ramamurthy | What state knowledge is worth when partitioning: the gap, the viability time, and the clock it is measured on |
| `partition_robustness.py` | in progress, joint with V. Ramamurthy | Does the effect survive system size and graph density? Two axes of the matrix |
| `partition_topology.py` | in progress, joint with V. Ramamurthy | Adds graph topology as a third axis — and finds that the measure the first two used depends on the circuit depth |
| `horizon_early_signal.py` | in progress, joint with V. Ramamurthy | How early a computation reveals how fast it will forget: static graph, then one observed layer, then more |
| `gate_vs_state_partition.py` | in progress, joint with V. Ramamurthy | Would a distributed compiler see what the horizon sees? A gate-based cut never moves in QAOA, and following the information cut costs more remote gates. Optional cross-check against the memQ DQC compiler |
| `entanglement_horizon.py` | in progress, joint with V. Ramamurthy | The horizon on a cost that is really paid: Schmidt dimension for distributed simulation. The first cut lasts far longer than H_v says, and keeping it costs a few percent |
| `second_circuit_family.py` | in progress, joint with V. Ramamurthy | Does the margin–horizon relation hold outside QAOA? Trotter as a second family, same definitions, effect sizes and bootstrap intervals |
| `staleness_cost.py` | in progress, joint with V. Ramamurthy | EO-2: a branching circuit whose later gates are not knowable at compile time. What it costs to keep a stale partition, five planners in one currency, and the latency at which reorganising stops paying |
| `drift_cost.py` | in progress, joint with V. Ramamurthy | EO-3: the same question with a drifting structure and no announcing bit. The horizon turns out to be a brake, not a steering wheel |
| `drift_robustness.py` | in progress, joint with V. Ramamurthy | Does the brake survive? Tolerance, drift rate and migration price swept, plus one deliberate run with noise on every network operation |
| `autonomous_entanglement.py` | in progress | What a dissipatively stabilised link buys a scheduler: concurrence to fidelity, the distillation cost, and whether the staleness inequality moves |
| `hypercube_vs_mps.py` | What a Node Actually Holds | Flat exchange against bond dimension; the crossover at S ≈ 1.4 |
| `routed_partition_orbit.py` | What the Computation Knows About Its Own Organisation | Whether the gate-optimal cut survives routing: transient and period of the layout orbit, and whether the cut holds over the cycle. Pre-registered in [designs/](designs/) before the first run |
| `orbit_edge_null.py` | in progress, joint with V. Ramamurthy | The matched-window control with the router's own move set: the published margin was an upper bound, and by how much |
| `diffusion_cut_arithmetic.py` | What the Operator Hides From the Partitioner | Why the diffusion operator looks unpartitionable and its standard decomposition is not: the V-chain's minimum balanced cut is eight gates at every size, and eight ebits per amplification iteration follow |
| `routed_diffusion_cut.py` | What the Operator Hides From the Partitioner | Whether a cut-oblivious compiler realises that cheap cut. It does not quite: about a factor of two above the logical minimum, flat across sizes, and withdrawn against the registered threshold |
| `diffusion_controlled_block.py` | What the Operator Hides From the Partitioner | What must cross a module boundary to apply the diffusion operator: one controlled-Z, not eight gates. Corrects the article's ledger by a factor of eight |
| `findability_scoping.py` | in progress | Whether a heuristic ever misses the enumerated optimum, and how many partitions reach it: the gap is small, the degeneracy is not. Registered in [designs/](designs/) as the note that follows it |
| `cut_degeneracy.py` | in progress | How many balanced bipartitions reach the exact minimum cut, how far apart they lie in migrated qubits, and how far two independent runs land from each other. Registered in [designs/](designs/) before the run |
| `cut_degeneracy_warmstart.py` | in progress | Whether a partitioner told where the qubits already are reaches the optimum as often, and moves fewer of them. The registered objective is withdrawn; the printout says on which ground |
| `resolution_limit.py` | in progress | Whether a difference is large enough to be a difference and whether the sample can tell: a declared granularity, a bootstrap over a declared unit, and verdicts that cannot come out blank. Registered in [designs/](designs/) before it was applied |
| `basket_grid_sensitivity.py` | What Moves the Baseline | Which half of a crossover does a modelling decision move? The crossover is a budget of oracle calls, not a problem size. Under grid truncation barely the classical half — about ±200 calls against a swing of some 18,000, and the swing itself is the measurement author's estimate, not a run, and not monotonic. Under correlation, the amount the amplitude predicts at 1/√a. A method check against an external measurement, not a QWeb result |
| `moving_baseline_figure.py` | What Moves the Baseline | Version 2: two panels, one per modelling decision. Version 1 put them on one axis and the article's central claim rested on that merger. Left the truncation estimate with the thin band the classical side accounts for, right the reported correlation move with an interval that contains zero. Every value copied from `basket_grid_sensitivity.py` with its provenance, and the published caption in the docstring |
| `partitioner_figure.py` | What the Partitioner Stops Solving | Figure 1: mean gap to the exact minimum balanced gate cut, against register size. Logarithmic, with a separate rail below it for the values that are exactly zero — plotting a true zero at a small positive value would be the quiet substitution the article is about. METIS hollow from n = 20, where some of its answers are no longer balanced and are excluded. Every value copied from `findability.py` and `findability_large.py` with its provenance, and the published caption in the docstring |
| `moving_baseline_teaser.py` | What Moves the Baseline | Version 2 of the teaser image, 1200×628 in the house design, rendered to `designs/teaser_moving_baseline.svg`. The motif shows the two decisions apart, as the figure does. Three numbers across the panel — one estimate, one ours, one reported — and the footer names the source |
| `findability.py` | What the Partitioner Stops Solving | Does a real partitioner find the minimum balanced gate cut? Kernighan–Lin reaches the exact optimum in all 21 published graphs and up to n = 24 — at twenty restarts; at one restart it misses two. METIS matches it and then leaves the balanced class from n = 20. The random balanced baseline the literature normalises against sits 119 % above the optimum at n = 10 and keeps rising |
| `findability_large.py` | What the Partitioner Stops Solving | The same question at n = 26 and n = 28, with a vectorised ground truth that is gated on agreeing exactly with `partition_topology` wherever both run — it did not, on first use, and the partition counts were exact while the contents were wrong. Kernighan–Lin holds the exact zero to n = 28; METIS is off by exactly one vertex at every size, in a share that does not grow with n |

A dash in the Article column marks a script that checks a published external
measurement rather than a QWeb article.

## A note on what these do and do not show

These scripts verify arithmetic. They do not verify the physics, the
architecture, or the conclusions drawn in the articles — those rest on
published results, which the articles cite, and on arguments the reader
is invited to disagree with.

If a number here does not match the article, the article is wrong.
Please say so.


## A note on the two QDNN scripts

Unlike the rest of this repository, these two do not verify arithmetic from
a published source. They are an experiment: the ablation study that the
article argues nobody runs. The numbers in that article come from these
scripts and nowhere else, so they are the ones most worth attacking.

`qdnn_ablation.py` takes about two minutes. `qdnn_sweep.py` takes four
arguments in turn — `2`, `4`, `8`, `16` — and about ninety seconds each.
`qdnn_replicate.py` takes a dataset name — `breast_cancer`, `wine` or
`digits` — and about two minutes each.


## A note on partition_information.py

This one is not settled. It belongs to work in progress with Venkateswaran
Ramamurthy on how much global state information a distributed scheduler
actually needs. The numbers in it are measurements from a single circuit
family at ten qubits, and they already tighten a figure quoted elsewhere on
the site — the scheduling bound in the architecture article assumed a
200-gate horizon, where this measures a viability time of well under a
microsecond — and the permissible separation comes out in tens of metres,
not kilometres.

Treat it as a record of where the experiment stands, not as a result.

`partition_robustness.py` is its companion: it varies system size and graph
density, and takes about three minutes. The short version is that the effect
survives both, and that individual graphs are not informative — only averages
over several are.

`partition_topology.py` is the third, and it is the one that corrects the other
two. Adding graph topology as an axis made it clear that the quantity all three
were measuring — the partition's lifetime, averaged over every starting layer of
an eight-layer circuit — cannot exceed what is left of the circuit, so it was
capped, and it moves with a depth nobody chose deliberately. Measured once from
the start of a circuit long enough not to cap it, the horizon settles, and the
picture changes in two ways worth knowing:

- the separation between graph structures is a factor of seventeen, not three;
- the permissible distance is tens of metres for a random interaction graph and
  around a kilometre for one with clear community structure. The figure quoted
  elsewhere on the site is the random-graph case, which is the shortest.

The numbers in the two earlier scripts are not comparable with this one, and
where they disagree, this one is the later measurement.

One open question now sits under all three. The horizon is measured on the
mutual information across a cut, which is a proxy. On the costs that are
actually paid - remote gates when a circuit is executed
(`gate_vs_state_partition.py`), Schmidt dimension when it is simulated
(`entanglement_horizon.py`) - the partition chosen at the start stays good far
longer, or never needs to change at all. Until it is clear which cost the
horizon bounds, read the distances above as a measurement of the proxy, not
as a limit on a network.

## designs/

Design notes for measurements, committed before the first computation, so
that the date on a hypothesis is a fact rather than a claim. Changes made
after the fact are dated addenda; the original text is never edited.

| Document | What it is |
|---|---|
| `design_routed_partition_orbit_EN.md` | The design, 16 October 2026 |
| `..._addendum_1.md` | Router regime and return-swap costs, 18 October |
| `..._addendum_2.md` | The permutation control came out degenerate; a replacement, 20 October |
| `routed_partition_orbit_run_2026-10-20.txt` | The printout of the first run |
| `routed_partition_orbit_run_2026-10-20_with_addendum_2_control.txt` | The same measurement with the replacement control |

If a printout contradicts a later text, the text is wrong.

## figures/

Scripts that draw the figures in the articles, kept apart from
`calculations/` because `run_all.py` runs everything it finds there.
Calculations check claims; figures draw them.

| Script | Article | Output |
|---|---|---|
| `qubit_bloch.py` | What a Qubit Actually Is | Bloch spheres emptying under a ZZ interaction — animated GIF plus five stills ([preview](figures/qubit_bloch_4_entangled.svg)) |
| `diffusion_cut_figures.py` | What the Operator Hides From the Partitioner | The constant cut, the compiler's factor, and where the diffusion sits beside two ordinary workloads — three SVGs ([preview](figures/diffusion_cut_figure_1.svg)) |

Generated output goes to `figures/out/` and is not tracked.

---

Ramon Schweiss · QWeb © Research · [qweb-quantum.com](https://qweb-quantum.com)
