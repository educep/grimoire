---
name: tdd
description: Test-driven development discipline. Red, green, refactor: one behavior at a time, tested through the public interface. Use when building a feature or fixing a bug test first.
---

# Test-driven development

Write one failing test for one behavior, watch it fail, write the least code that makes it pass, then refactor. Do the next behavior the same way. Don't write all the tests up front and then all the code; tests written in bulk only check behavior you imagined, and they tend to pin down the shape of things rather than what the user actually needs. Let each test follow from what the last cycle taught you. The test comes first, never bolted on afterwards.

## What a good test looks like

It checks behavior through the public interface, the same entry point a real caller uses, and ignores whatever sits behind it. It reads like a specification ("a user can claim a reward once per session") and stays unchanged when you rework the code underneath.

Assert the whole value, not its shape. Compare against the full result, `toEqual(['a', 'b'])` or the complete object, not a loose `typeof x === 'object'` or "the list isn't empty". The expected value has to come from somewhere independent: a literal you know is correct, a worked example, the spec. If you build it the same way the code does, the test passes by construction and proves nothing.

## What to avoid

Mocking your own modules. Testing private helpers. Asserting how often or in what order something was called. Reading the result through a side channel instead of the public interface. The tell is a test that breaks when you rename an internal function even though the behavior never changed; that test was measuring the implementation.

## Mocking

Mock only at the edges: outside APIs, the clock, randomness, and, sparingly, heavy services like a database or a queue where a real instance is better when you can run one. Never mock code you own. Keep the edges swappable by passing dependencies in instead of building them inside, and give each external call its own small interface so a mock returns one fixed shape with no branching.

## Refactor only on green

Once the tests pass, tidy up: remove duplication, hide complexity behind a small interface, move logic next to the data it uses, and run the tests after each step. Never refactor while a test is red. Get to green first.

Before you move on, a test should describe behavior rather than implementation, use only the public interface, survive a refactor, assert an independent value, and rest on the least code needed to pass, with nothing speculative added.
