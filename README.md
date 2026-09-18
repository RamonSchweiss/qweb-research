# QWeb © Research — Calculations

Every figure and every number quoted in the articles at
[qweb-quantum.com](https://qweb-quantum.com) comes from a calculation.
This repository holds those calculations so that anyone can check them.

Each script is standalone, prints its results, and states which article
and which figure it belongs to. Nothing is hidden in a library.

## Requirements

```
pip install numpy scipy scikit-learn pennylane
```

Nothing else. The scripts are deliberately plain: no notebooks, no
plotting dependencies, no framework. They print numbers you can compare
against the articles.

## Running everything

```
python run_all.py          # the quick checks, about five seconds
python run_all.py --all    # including the QDNN experiment, about two minutes
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
| `hypercube_vs_mps.py` | What a Node Actually Holds | Flat exchange against bond dimension; the crossover at S ≈ 1.4 |

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

---

Ramon Schweiss · QWeb © Research · [qweb-quantum.com](https://qweb-quantum.com)
