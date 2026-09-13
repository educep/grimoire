---
name: tdd
description: Test-driven development discipline. Red, green, then refactor, one behavior at a time, tested through the public interface. Use when building a feature or fixing a bug test first.
---

# Test-driven development

Write one failing test for one behavior, watch it fail, write the least code that makes it pass, then refactor. Do the next behavior the same way. Don't write all the tests up front and then all the code; tests written in bulk only check behavior you imagined, and they tend to pin down the shape of things rather than what the user actually needs. Let each test follow from what the last cycle taught you. The test comes first, never bolted on afterwards.

## What a good test looks like

It checks behavior through the public interface, the same entry point a real caller uses, and ignores whatever sits behind it. It reads like a specification ("a user can claim a reward once per session") and stays unchanged when you rework the code underneath.

Assert the whole value, not its shape. Compare against the full result — the complete list, the complete object — not a loose type check or "the list isn't empty". The expected value has to come from somewhere independent: a literal you know is correct, a worked example, the spec. If you build it the same way the code does, the test passes by construction and proves nothing.

## What to avoid

Mocking your own modules. Testing private helpers. Asserting how often or in what order something was called. Reading the result through a side channel instead of the public interface. The tell is a test that breaks when you rename an internal function even though the behavior never changed; that test was measuring the implementation.

## Mocking

Mock only at the edges: outside APIs, the clock, randomness, and, sparingly, heavy services like a database or a queue where a real instance is better when you can run one. Never mock code you own. Keep the edges swappable by passing dependencies in instead of building them inside, and give each external call its own small interface so a mock returns one fixed shape with no branching.

## A test is not evidence until it has been shown to fail

Watching the test fail first is the whole point of red-green, and it is the step most often skipped
when a test is added *after* the fact — to pin a bug fix, or to satisfy a reviewer. Four separate
tests in one run could not fail at all, and none was found by reading:

- **The tautology.** An assertion that compares the guard's own result against the very
  predicate the guard is implemented with. It compares an implementation with itself. Assert the independent
  fact instead — the status set, the worked number, the spec.
- **The wrong branch.** A control that neutralizes a *neighbouring* flag proves nothing about the
  branch under test. One fixture exercised a code path whose branch could not observe the defect it
  was written for; it stayed green under a full revert of the fix.
- **The unparametrized arm.** A conditional shipped with two arms and a fixture for one. "N passed"
  is not coverage of a branch nobody parametrized — and the untested arm carried two catastrophes.
- **The harness-blind assertion.** A claim the runner is *configured* not to observe: a schema
  migration verified against a runner that skips migrations, a commit-time callback asserted
  inside a test transaction that never commits. Correct-looking and broken-looking are identical.

So: **for each new conditional, name the fixture that takes each arm.** If you cannot, that arm is
untested. And before trusting any test written to catch a specific defect, break the fix and watch
that test — and only that test — go red.

Three refinements on "break it and watch it redden", each of which caught a test that could not
fail while its author believed it had been proved:

- **Mutate to a WRONG VALUE OF THE SAME SHAPE, not to absence.** A deletion probe is structurally
  blind to a value that is *present but wrong*: deleting changes the shape, and any incidental shape
  check reddens for a reason unrelated to the assertion under audit. One 28-row deletion matrix
  scored an ordering assertion green because deletion tripped a length check, while that same
  assertion was simultaneously accepting three different wrong orderings. *"27 of 28 reddened"* was
  true and was not the same claim as *"27 of 28 are evidence"*.
- **A REPAIRED assertion is a new claim — run it against unmodified code before trusting it.**
  Strengthening a weak assertion means writing a stronger claim about what correct code produces,
  and that claim can be wrong in a new way. A fix round that only re-runs the red case replaces a
  decorative assertion with a false one. Assumptions about *rendered* output — generated queries,
  serialized payloads, template text — are claims to measure, never to derive from the source that
  produces them.
- **A bounded predicate has TWO edges; pin the one you are not thinking about.** Any exception
  guard, rate limit, allowlist, status set or numeric range has an upper edge (what it must not let
  through) and a lower edge (what it must not absorb). A finding points at one of them, and that is
  the edge you will pin — so **write the other edge's test in the same commit**. One guard, narrowed
  to the class a reviewer pointed at, absorbed the failure it was aimed at and let a *sibling* class
  of the same parent crash the page the guard existed to protect: one word too narrow, in the
  direction nobody had written a test for.

## The fix and its proof share a path

Name **every route** a behaviour has — preview vs. commit, per-tenant, per-locale, per-outcome —
and assert on all of them, with **measured integers, never `<=` bounds**. A test whose fixture
cannot produce the failing case proves nothing, and it will be green precisely because the fixture
lacks the case. Two corollaries:

- **Fixture provenance.** A test asserting a payload or interface shape builds its fixture by
  calling the real producer (or pinning the producer's declared fields) — never by hand-rolling the
  dict, which quietly asserts your guess against your guess. The deepest defects survive multiple
  reviews behind an invented fixture.
- **A discriminating input, or nothing.** For every assertion, name an input on which the correct
  and the incorrect implementation *differ*. A corpus where both land on the same answer — supply
  always covering demand, a worked example where either branch picks the same value, all-rejection
  candidates — cannot distinguish them, and **the absence of such an input from the corpus is a
  finding, not a gap**. Boundary values can hide a guard entirely (a zero multiplier pins nothing).
- **A fixture's type comes from the production declaration, not from what reads nicely.** A guard
  against a bad coercion was handed the one input type for which that coercion happens to succeed.
- **A probe that asserts an AXIS varies only that axis, between two otherwise-identical callers.**
  One caller plus a status code measures every gate at once and attributes the answer to whichever
  one you had in mind. One probe took three corrections before it measured anything: restricted to a
  verb twelve doors do not accept; then using a verb that resolves no action, so every override took
  its fallback branch and the probe measured a branch no real caller reaches; then comparing raw
  status codes, which a *different* axis's gate also produces. What worked: two callers differing
  only on the axis, compared on refusal-ness rather than on the exact code. **And a probe returning
  zero proves nothing until it has returned non-zero on a known positive** — one reported "nothing
  found" because its own marker was being escaped.
- **Delete the non-code the behaviour depends on, and run the suite.** For every attribute, markup
  element, ordering of decorators or explanatory sentence a behaviour rests on: remove it and see
  what reddens. One sweep found seven behaviours — a security header, an event target, a hidden
  field, a decorator's position — each deletable with the whole suite green.
- **Write the pin against the known-good baseline and watch it redden BEFORE the change touches the
  file.** A pin written afterwards only describes what the change produced. The one pin written
  ahead of a rewrite caught a dependency that ten existing tests would have stayed green through
  losing.
- **A guard's self-test may not mutate the tree the other tests are reading.** Planting a violation
  into the real source roots passes alone and reddens an unrelated census the moment the suite runs
  in parallel — the failure surfaces far from its cause, in a file nobody touched. Plant in a
  temporary tree instead, and prove the ROOTS separately: one assertion that the scanner finds a
  planted violation in a temp tree (the walk and the pattern work), one that each declared root
  resolves to a real directory containing the kind of file scanned (the roots are not typos).
  *Corollary of the same shape*: a source-scanning guard must skip comments, or it flags its own
  documentation — a comment explaining a defect necessarily spells the defect — and teaches the next
  author to delete the documentation.

## Absence is not behaviourally testable

Deleting what nothing reads changes no behaviour, so no behavioural test can pin the deletion.
Absence fixes ship with a **source scan plus a self-test proving the scanner can fail** (plant the
violation, watch the scan redden, remove it) — otherwise re-adding the removed thing leaves the
whole suite green. The scanner's claimed scope is itself under test: one planted violation per
claimed root. The same discipline covers any **gate command** you are about to trust for the
first time — a syntax checker, a linter invocation, a census script: feed it an input that must
fail and watch it fail, because more than one stock checker exits 0 without examining anything.

## When examples keep losing, assert the invariant

Attribution-shaped defects are invisible to totals: every version summed correctly and only
mis-destined the units, so each hand-written fixture stayed green and four fix rounds each closed
exactly the gap the previous review had named. What ended it was **a property test** — the
invariant asserted over randomized interleavings — which also surfaced a second bug nobody was
looking for. When example-based rounds converge one gap at a time on the same defect, stop writing
examples. Prefer asserting over the governing **constant or registry**, so a case added later is
covered without anyone remembering to come back — except where the test exists to check the
constant itself, in which case a deliberate hand copy is the point; say which one you are doing.

Two habits keep coverage claims honest: a guard's own documentation records what it is
**measured** to catch — including what is structurally invisible to it — and a test's coverage
claim names the **surface it exercises** (driving the endpoint directly proves nothing about
the button that is supposed to reach it). Documentation asserting its own untestability is a
defect-preserving construct, not a disclaimer.

## Refactor only on green

Once the tests pass, tidy up: remove duplication, hide complexity behind a small interface, move logic next to the data it uses, and run the tests after each step. Never refactor while a test is red. Get to green first.

Before you move on, a test should describe behavior rather than implementation, use only the public interface, survive a refactor, assert an independent value, and rest on the least code needed to pass, with nothing speculative added.
