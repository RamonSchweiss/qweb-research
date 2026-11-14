# Design note: what the standard QCNN benchmark can distinguish

**Registered 14 November 2026, before the first computation.**
Ramon Schweiss, QWeb © Research. No measurement has been run against this
question. Any change made after the first run is a dated addendum; this text
is not edited.

---

## 1 The claim being checked, and whose it is

Bermejo, Braccia, Rudolph, Holmes, Cincio and Cerezo (arXiv:2408.12739,
August 2024, v2 February 2026) attribute the heuristic success of quantum
convolutional neural networks to two things rather than one. A randomly
initialised QCNN can only use information from low-bodyness measurements of
its input states; and the datasets it is usually benchmarked on are
"locally-easy", meaning their states can be classified from that same
low-bodyness information.

The second half is a claim about the **benchmark**, not about the
architecture. It says the instrument on which QCNNs are judged cannot
distinguish a model that needs a quantum computer from one that does not.
That is the question this study measures, at a size one person can run.

This is a reproduction of someone else's claim at small scale, not an
independent discovery, and it must be cited that way wherever it is used.

One deliberate difference in method. They estimate the low-bodyness
quantities with Pauli shadows from measurements. This study computes them
exactly, from exact ground states. That is the easier condition for the
classical arm: it removes shot noise entirely. So if the classical arm fails
anywhere, the failure cannot be blamed on sampling.

## 2 The question

On the standard phase-classification benchmark, does a classifier restricted
to Pauli features of bodyness k ≤ 2 reach the test score of a trained QCNN,
within a declared resolution?

Out of scope, named here so that it is not quietly imported later: whether a
QCNN remains classically simulable **after** training. Cerezo et al.
(arXiv:2312.09121, v3 25 August 2025) state that the subspace QCNNs occupy is
effective and not proper, and may shift during training. Nothing in this
design addresses that, and no result from it may be read as addressing it.
Also out of scope: the cost of cutting a QCNN's hierarchical reduction across
modules. That is a separate question and gets a separate note.

## 3 Arms

1. **QCNN.** Convolution and pooling layers in the structure of Cong, Choi
   and Lukin (2019), depth L = log₂ n, two-qubit blocks on neighbouring
   qubits, trained by gradient descent on a linear cost.
2. **Bodyness-2 classifier.** Logistic regression on the exact expectation
   values of all Pauli operators of weight ≤ 2 on the same states.
3. **Bodyness-1 classifier.** The same, restricted to weight 1. A negative
   control: a feature set that is expected to be insufficient, included so
   that the classical arm is not assumed adequate by construction.
4. **Bodyness-4 classifier.** The same, weight ≤ 4. Used only in the
   positive-control dataset, to test whether a gap found there is a bodyness
   effect rather than a model-class effect.

## 4 Datasets

**D1, the benchmark under test.** Transverse-field Ising ground states at
n ∈ {8, 10, 12}, exact diagonalisation, field swept across the critical
point, labelled by phase. This is the dataset the claim is about.

**D2, the positive control.** A cluster-model family whose label depends on a
string order parameter longer than two sites. Here the bodyness-2 classifier
is **expected to fail** while the QCNN succeeds.

D2 is not decoration. Anyone reporting that two arms agree owes a
demonstration that the same comparison, run the same day with the same code,
can register a disagreement. Without D2, a finding of "the classical arm
matches" is indistinguishable from "this comparison cannot tell anything
apart".

## 5 The four declarations

Stated without reference to the architecture, so that they travel.

**Granularity.** The smallest nonzero difference the score can take is
1/m_test, by definition of a count of correct classifications over a test set
of m_test items. With m_test = 200 per draw, granularity is 0.005.

**Bounds, per arm.** The floor of the score is the majority-class share of
the test set, not 0.5, and it is recorded per draw. The ceiling is 1.0. The
two classical arms and the QCNN share these task bounds — but they do **not**
share a spread floor, and that is declared separately per arm: the QCNN's
spread is measured over random starts and dataset draws, the classical arms'
over dataset draws alone, because their solver is deterministic. Declaring
one spread for both would be the defect of case 6 in "What a Verdict
Assumes".

**Unit of analysis.** The dataset draw, of which there are 20 — not the
individual state, of which there are thousands. A bootstrap resamples draws.

**Minimum units.** Below 5 usable draws at a given n, the verdict for that n
is **not evaluable**, not "unresolved" and not "equivalent".

## 6 The resolution rule, and the trap it exists to block

The comparison reports one of four verdicts per dataset and size:
**separated**, **bounded**, **unresolved**, **not evaluable**. They are kept
apart in the printout and never merged.

The trap: hypothesis H1 below is satisfiable by a large noise floor. An arm
that cannot be told apart from another because the measurement is coarse is
not an arm that performs equally. Therefore:

> A verdict of "equivalent" is not available at all. Where the arms cannot be
> separated, the result is reported as **bounded above by** the measured noise
> floor, with that floor printed next to it. If the floor exceeds 0.05 in
> accuracy, the verdict is **not evaluable** regardless of the point
> estimates.

## 7 Registered hypotheses

- **H1.** On D1, the bodyness-2 classifier is not separated from the QCNN,
  and the bound is below 0.05.
- **H2.** On D2, the bodyness-2 classifier is separated from the QCNN,
  falling below it.
- **H3.** On D1, the QCNN's own spread over random starts exceeds the gap
  between the two arms.
- **H4.** On D2, the bodyness-4 classifier closes a substantial part of the
  gap that the bodyness-2 classifier shows — that is, the gap is a property
  of the feature bodyness and not of logistic regression as a model class.
- **H5.** On D1, the bodyness-1 classifier is separated from the QCNN. If it
  is not, D1 cannot distinguish any of these arms and the dataset is reported
  as such.

H2 and H5 are the two that can embarrass the study, and they are registered
for that reason. H1 is the convenient one.

## 8 Invalidating conditions

Any of these voids the run. They are written now so that they cannot be
written later.

1. **The positive control fails.** If H2 does not hold — the bodyness-2
   classifier matches the QCNN on D2 as well — the comparison cannot
   distinguish a locally-easy dataset from one that is not, and no statement
   about D1 may be made from it.
2. **The QCNN does not train.** If the QCNN's score on D1 sits at the
   majority-class floor, there is no trained model to compare against, and
   the run is void rather than a tie.
3. **The ground truth is not verified.** Exact ground states must agree with
   an independent slower construction at the smallest size, element by
   element and not by norm or by count. Counting the right number of things
   is not the same as having the right things.

## 9 Stopping condition, independent of the result

20 dataset draws, 5 random starts per draw for the QCNN, at n ∈ {8, 10, 12},
on both D1 and D2. The run stops there whether or not any hypothesis has
resolved, and no draw, start or size is added afterwards. If the result is
unresolved at that budget, "unresolved at 20 draws" is the finding.

## 10 What this cannot show

It cannot show that QCNNs are useless; the claim is about one benchmark
family. It cannot show anything about real-world data, since both datasets
are generated from a Hamiltonian. It cannot speak to the trained regime, as
§2 says. And it cannot establish that the benchmark was *chosen* because it
is locally easy — only that it is.

A result in favour of H1 would be a statement about an instrument, not about
an architecture. That distinction is the whole point and must survive into
the write-up.

---

**Sources fixed at registration**

- Pesah, Cerezo, Wang, Volkoff, Sornborger, Coles, *Absence of Barren
  Plateaus in Quantum Convolutional Neural Networks*, PRX 11, 041011 (2021),
  arXiv:2011.02966. Variance lower bound Ω(1/poly(n)); the polynomial comes
  from depth L = log n, under independent 2-design blocks and a linear cost.
- Cerezo, Larocca, García-Martín et al., *Does provable absence of barren
  plateaus imply classical simulability?*, arXiv:2312.09121 v3, 25 August
  2025. QCNNs named in Table 1, effective and not proper polynomial
  subspace.
- Bermejo, Braccia, Rudolph, Holmes, Cincio, Cerezo, *Quantum Convolutional
  Neural Networks are Effectively Classically Simulable*, arXiv:2408.12739,
  August 2024, v2 February 2026. Pauli-shadow simulation to 1024 qubits on
  phase classification; "locally-easy" benchmarks.
- Cong, Choi, Lukin, *Quantum Convolutional Neural Networks*, Nature Physics
  15, 1273 (2019). The architecture the QCNN arm follows.
