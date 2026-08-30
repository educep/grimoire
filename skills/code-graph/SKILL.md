---
name: code-graph
description: Build and use a structural graph of the project's own code to answer reachability questions cheaply — can X actually produce Y, who calls this, what consumes that. Use before an expensive manual census, and whenever a claim depends on what reaches what. Ships a working language-agnostic builder. Optional: it needs a tool install.
---

# Code graph

A structural graph of the project's own symbols and the edges between them. It makes the
expensive questions cheap: **reachability** (*"can X actually produce Y?"* — the causal half of a
compound claim), call-site censuses, consumer hunts.

> **Adapter first.** Read the adapter's `code-graph` capability: how this project builds the graph,
> how it checks staleness, where the output lives, and **what its generator cannot see**. If the
> capability is absent, this skill does not apply — answer the question the expensive way and say
> that you did. It is optional under the contract's test: it requires installing a tool the project
> does not otherwise need.

______________________________________________________________________

## The one rule that makes an imperfect graph safe

> **It may only ever ADD candidates to check. It is NEVER evidence for a negative.**

*"Nothing calls X"* is precisely the conclusion it cannot support, and precisely the one that
deletes live code. Every answer is a **lead** — a superset to verify by reading or running, never a
finding on its own.

What a structural graph cannot see, in any language: templates and other non-code call sites,
runtime registration (signals, task autodiscovery, plugin loaders), reflective and string-keyed
dispatch, dependency injection, and anything constructed at runtime. Those absences are exactly
where a confident negative would be wrong.

______________________________________________________________________

## Check freshness before trusting anything

A graph is derived and decays on **every** commit. An answer from a stale graph arrives with exactly
the same confidence as an answer from a fresh one — which is what makes staleness dangerous rather
than merely inconvenient.

So the check is unconditional and comes first. The bundled builder reports STALE in three cases, and
the third is the one people miss:

1. no graph at all;
2. the graph's stamped commit differs from `HEAD`;
3. **the stamp matches `HEAD` but tracked files are dirty** — the graph matches the commit and still
   does not describe what is on disk.

It exits `0` for fresh and `1` for stale or missing, so it works as a gate in a script.

______________________________________________________________________

## The bundled builder

`scripts/build_code_graph.py` is a working reference implementation, and the only executable file in
this package — everything else is prose. It is **language-agnostic**: graphify's own `detect` and
`extract` carry the tree-sitter grammars, so the wrapper never names a language.

```
python scripts/build_code_graph.py            # whole repo
python scripts/build_code_graph.py --check    # staleness only, builds nothing
python scripts/build_code_graph.py --path src/a src/b     # scoped build
```

Set `CODE_GRAPH_OUT` to change the output directory (default `graphify-out`).

Prerequisite: `uv tool install graphifyy` (or pipx). The script runs under **any** Python — it
locates the standalone tool install and re-execs itself under it, so a project venv without graphify
is fine.

**Three things it does deliberately, each because the naive version failed:**

- **Code only, no LLM.** graphify's default pipeline runs semantic extraction over every document
  and image, which costs real money and encodes *prose* into the graph. A graph of claims is not a
  verification instrument.
- **It PROVES an interpreter before handing off**, rather than checking that the path exists. A
  `uv tool install`'s launcher can exist on disk and still fail, because it re-execs into a base
  CPython recorded in its own config — and that base can be removed by a version bump without
  touching the tool venv. Only running it proves the chain. *(Measured: this exact failure made a
  graph silently unavailable for weeks; `Path.exists()` said yes and the interpreter was gone.)*
- **It refuses to write an empty or shrunken graph**, rather than overwriting a good one with a
  broken run.

______________________________________________________________________

## Never commit the output

It is derived, and it decays on every commit. A committed graph is a confidently-stale answer
source that outlives everyone's memory of when it was built. Gitignore the output directory.

______________________________________________________________________

## Scope for readability

Above ~5,000 nodes graphify's HTML export aggregates: every dot becomes a community rather than a
symbol, losing names, files and line numbers. The JSON keeps full per-symbol detail either way, so
this only affects browsing. For a readable node-level picture of a large codebase, build the
subsystem you are working on with `--path` rather than the whole repo.
