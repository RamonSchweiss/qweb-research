# Addendum 3: the rerun, and the objective withdrawn on both families

**Date:** 1 November 2026. Records the rerun authorised by Addendum 2, which was
committed before it. The note remains in force and is not altered, and
Addendum 1's grid verdict is not recounted: the registered sizes and the sizes
added by Addendum 2 are reported apart, as Addendum 2 section 7 required.

**The rerun.** `calculations/routed_diffusion_cut.py` with the register range at
n ≤ 13, output in `designs/routed_diffusion_cut_output.txt`. Everything else as
declared: the V-chain decomposition, both generators and the heavy-hex(5) host,
SABRE with the decay heuristic, the trivial initial layout, the five seeds, both
degeneracy rules, the contrast families, and the stopping condition with its
threshold of 0.05.

---

## 1 The heavy-hex arm now speaks, and it says the same thing

Both sizes added by Addendum 2 are non-degenerate, as it predicted: 22 and 24
node subgraphs with two independent rings each.

      topology    P     r-m   threshold   margin   spread   margin/spread
     heavy-hex   22   0.048       0.050   +0.002    0.008            0.25
     heavy-hex   24   0.063       0.050   -0.013    0.022           -0.59
          grid   12   0.083       0.056   -0.027    0.056           -0.48
          grid   16   0.089       0.080   -0.009    0.080           -0.11
          grid   18   0.084       0.064   -0.020    0.064           -0.31
          grid   20   0.067       0.050   -0.017    0.041           -0.41
          grid   24   0.053       0.050   -0.003    0.038           -0.08

The first five rows are the sizes the note registered. The last two columns are
not part of the stopping condition and are given because of section 2.

## 2 The one apparent retention is a withdrawal under section 11

The inequality of section 10 retains the objective at heavy-hex P = 22, by a
margin of 0.002. The script prints that verdict, and the committed printout
says "retained at 1 of 2". Section 11 of the note, written before any run,
says:

> No threshold is adjusted after the run. An outcome close to one is reported
> as close to it and treated as a withdrawal.

A margin of 0.002 on a threshold of 0.05 is close to it. **The objective is
therefore withdrawn at heavy-hex P = 22 as well, and at all seven decidable
sizes.**

**The clause is applied symmetrically, and that is visible in the table.** Grid
P = 24 misses the threshold by 0.003 — closer, on the other side. Both sizes
are inside three thousandths of the line, one either way, and section 11
resolves both as withdrawals. The clause is not being reached for because it
gives the convenient answer; it would have been quoted for the grid row too.

**What section 11 did not say, and is not being made to say now.** It does not
quantify "close". One natural quantification is visible in the table: at
heavy-hex P = 22 the margin is a quarter of the seed spread, so the retention
is not resolved by the measurement that produced it. That reading is offered
for inspection and **was not a rule in force during this run**, and declaring
it now — after seeing that it turns the only retention over — would be
adjusting a rule to a result. If it is to apply mechanically, it belongs in an
addendum agreed before the next run, not in this one.

The judgement, then, is a judgement that section 11 reserved, exercised here
and shown with the numbers that provoked it.

## 3 What replaces the objective, now on two families

The registered objective — that a cut-oblivious router lands close to the
logical minimum of eight — does not hold anywhere it could be tested. What is
measured instead is a factor, and the two topology families agree on it:

      grid        1.88   2.25   2.62   2.25   2.25
      heavy-hex   2.38   3.00
      mean over the seven decidable sizes:  2.38

**A cut-oblivious router costs about a factor of 2.4 on the diffusion's cut,
and the factor does not depend on which of the two coupling-map families it
runs on.** The ranges overlap; the two heavy-hex values are two points and not
a trend, as Addendum 2 section 5 insisted in advance.

Addendum 1 reported this factor as 2.25 from the grid alone. The second family
moves it to 2.38 and, more usefully, removes the possibility that it was a
property of grids.

## 4 The contrast, and the strongest single result of the rerun

At P = 24, with both families now available:

                     grid      heavy-hex
      community     0.027          0.067
      the diffusion 0.096          0.094
      regular       0.111          0.112

Three things in one table. The diffusion sits between two ordinary sparse
workloads on **both** families. A 3-regular graph is more expensive to cut than
it, on both. And the diffusion's own crossing fraction is nearly the same on
the two topologies — 0.096 against 0.094 — where the comparison workloads
differ between them by a factor of up to two and a half.

The operator that version 1 of the note called the limiting case of circuit
partitioning turns out to be the workload least sensitive to the coupling map
of the three measured. That is the opposite of the original claim in a second,
sharper sense than Addendum 1 could show.

## 5 The ledger entry, corrected again

Eight ebits per iteration is the logical minimum under free placement.
Addendum 1 put the routed figure at about 18 from the grid alone. With both
families it is about **19**.

       n   iterations   at 8 per iteration   at 19 per iteration
      16          201                1,608                 3,819
      20          804                6,432                15,276
      30       25,735              205,880               488,965

Still an extrapolation of a factor measured only up to P = 24, that is to
thirteen data qubits. A 16-qubit Grover needs P = 30. What is measured is that
the factor is in the same band on two families and over seven sizes; whether it
stays there beyond P = 24 is not established.

## 6 What stands after this addendum

- Sections 3 and 4 of the note are untouched: the V-chain's logical minimum
  balanced cut is eight gates at every size, and the ancilla-free synthesis has
  a complete interaction graph.
- The routing objective of section 6 is **withdrawn on both families**, at all
  seven decidable sizes, two of them within three thousandths of the threshold
  and resolved by section 11.
- What replaces it is a measured factor of about 2.4, consistent across the two
  families and the seven sizes.
- The ledger is 19 ebits per iteration routed against 8 under free placement,
  and the gap between those two numbers is a statement about compilation rather
  than about the algorithm.

## 7 What this still does not establish

A cut-aware router. SABRE minimises total swaps and not swaps across a
boundary, so 2.4 bounds what a router told about the boundary would cost and
says nothing about what it could achieve. This is the invalidating condition of
section 8 and it applies to every number above.

One router, one heuristic, one initial layout. Two coupling-map families, one of
which contributes only two sizes. Degenerate sizes excluded by a rule that
removed eight of ten heavy-hex sizes, which is a comment on the family's local
geometry and not on the operator. And the oracle remains uncounted.

## 8 Consequence for the article

"What the Operator Hides From the Partitioner" now rests on three findings,
each with its own measurement and all three published whichever way they came
out:

1. The operator's form says the workload cannot be partitioned; its standard
   decomposition contradicts that at a constant eight gates, and the ancilla
   count is what buys the difference.
2. The decomposition nobody uses is where the operator's form tells the truth,
   so the field's choice already answered the question the hypothesis asked.
3. Compilation costs about a factor of 2.4 on top of that, consistently across
   two coupling-map families — and even then the diffusion is cheaper to cut
   than a 3-regular graph, and less sensitive to the coupling map than either
   comparison workload.

The third finding is the only one that needed a measurement, and the
measurement withdrew the objective it was registered to test. The article says
that, with the dates.
