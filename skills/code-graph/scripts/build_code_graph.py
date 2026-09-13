"""Build the structural code graph, code-only, and report its staleness.

Language-agnostic: graphify's own ``detect``/``extract`` handle the tree-sitter
grammars, so this wrapper never names a language. It is the reference
implementation of the adapter's ``code-graph`` capability, and the only file in
this package that is executable rather than prose.

Why this rather than a bare ``graphify .``
------------------------------------------
graphify's default pipeline dispatches semantic (LLM) extraction over every
document and image it finds -- parallel subagents, minutes of wall clock, and
real token cost. It also encodes *prose* into the graph, which is worse than
useless for verification: prose is the thing you cannot trust, and a graph of
claims is not a verification instrument.

This takes the code-only path: AST extraction, deterministic, no LLM, no API
key, no network.

Run it with ANY python -- including a project venv that does not have graphify.
The script locates the standalone tool install (``uv tool install graphifyy`` or
pipx) and re-execs itself under it. graphify is dev tooling and should never
become a runtime dependency, which is why it is not expected in your project's
requirements.

Usage
-----
    python <this-script>                  # whole repo
    python <this-script> --check          # only report staleness, build nothing
    python <this-script> --path src/a src/b
                                          # SCOPED build

Set ``CODE_GRAPH_OUT`` to change the output directory (default ``graphify-out``).

Scope matters for the HTML view. graphify aggregates above 5,000 nodes: every
dot becomes a community rather than a function, losing names, files and line
numbers. A whole-repo build on a large codebase is past that, so for a browsable
node-level picture, build the subsystem you are working on. The JSON always
carries full per-symbol detail -- only the HTML aggregates.

``--check`` exits 0 when the graph matches ``HEAD``, 1 when it is stale or
missing. It is safe to run anywhere, touches nothing, and is the call to make
BEFORE trusting any answer the graph gives. It reports STALE when the stamp
differs from HEAD **and** when the stamp matches but tracked files are dirty --
a graph that matches the commit still does not describe what is on disk.

Output is **gitignored on purpose** -- the graph is derived and decays on every
commit, so a committed copy is a confidently-stale answer source.

READ the adapter's ``code-graph`` capability BEFORE USING THE RESULT. The short
version, because it is the part that can actually hurt you:

    The graph is a SUPERSET GENERATOR. It may only ever ADD candidates to check.
    It is never evidence for a negative -- "nothing calls X" is precisely the
    conclusion it cannot support, and precisely the one that deletes live code.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

OUT = Path(os.environ.get("CODE_GRAPH_OUT", "graphify-out"))
GRAPH = OUT / "graph.json"


#: Bound on each candidate probe, so a broken interpreter (hung DLL load, a trampoline
#: stuck retrying a missing network path, etc.) cannot hang the tool -- it just fails
#: that candidate and moves on.
_PROBE_TIMEOUT_SECONDS = 10


def _reexec_with_graphify() -> None:
    """Re-run this script under an interpreter that HAS graphify, if this one lacks it.

    graphify is installed as a standalone tool (``uv tool install graphifyy`` or pipx),
    NOT into the project venv -- it is dev tooling, not a runtime dependency, and adding
    it to requirements.txt would ship it to production for no reason. But every other
    tool in this repo is run with the project venv's python, so a plain
    ``python <this-script>`` would die on ModuleNotFoundError and read as
    "the script is broken".

    So: locate the tool interpreter and hand off to it. Callers never need to know which
    Python owns graphify.

    Candidates are PROVEN, not merely checked for existence. A ``uv tool install``'s
    ``Scripts/python.exe`` is a trampoline launcher: it can exist on disk and still fail
    to run, because it re-execs into a base CPython recorded in its own ``pyvenv.cfg`` --
    and that base install can go missing (a `uv python` version bump or uninstall)
    without touching the tool venv itself. ``Path.exists()`` sees the trampoline and
    says yes; only actually running it proves the whole chain works. Each existing
    candidate gets a short, bounded ``-c "import graphify"`` subprocess probe; only a
    clean (returncode 0) probe is handed off to via ``os.execv``. A candidate that fails
    the probe -- missing base interpreter, broken venv, or a hang past the timeout -- is
    skipped in favor of the next one, instead of handing off into a broken process (which
    on Windows can print an OS error and still exit 0, reading as success while doing
    nothing).
    """
    try:
        import graphify  # noqa: F401

        return
    except ImportError:
        pass

    candidates: list[Path] = []
    for env in ("UV_TOOL_DIR", "PIPX_HOME"):
        base = os.environ.get(env)
        if base:
            candidates.append(Path(base) / "graphifyy" / "Scripts" / "python.exe")
    home = Path.home()
    candidates += [
        home / "AppData/Roaming/uv/tools/graphifyy/Scripts/python.exe",
        home / ".local/share/uv/tools/graphifyy/bin/python",
        home / ".local/pipx/venvs/graphifyy/Scripts/python.exe",
        home / ".local/pipx/venvs/graphifyy/bin/python",
    ]
    for c in candidates:
        if not c.exists():
            continue
        try:
            probe = subprocess.run(
                [str(c), "-c", "import graphify"],
                capture_output=True,
                timeout=_PROBE_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode != 0:
            continue
        # S606: intentional. This is a self-handoff to an interpreter we just PROVED can
        # import graphify -- no shell, no user input in the argv.
        os.execv(str(c), [str(c), __file__, *sys.argv[1:]])  # noqa: S606 - never returns

    print(
        "ERROR: graphify is not importable and no tool install was found.\n"
        "  Install it once (it is dev tooling, deliberately NOT in requirements.txt):\n"
        "      uv tool install graphifyy\n"
        "  Searched (each candidate that exists on disk was PROBED by actually running "
        "it, not merely checked for existence): " + ", ".join(str(c) for c in candidates),
        file=sys.stderr,
    )
    raise SystemExit(2)


def _head() -> str | None:
    """Current HEAD sha, or None outside a git work tree."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _dirty() -> bool:
    """True when tracked files differ from HEAD (so the graph cannot match anything)."""
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(r.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check() -> int:
    """Report whether the graph is usable. Exit 0 = fresh, 1 = stale/missing."""
    if not GRAPH.exists():
        print(f"STALE: no graph at {GRAPH} — run `python <this-script>`")
        return 1

    stamp = json.loads(GRAPH.read_text(encoding="utf-8")).get("built_at_commit")
    head = _head()
    print("graph built_at_commit: " + (stamp or "(unstamped)"))
    print("HEAD                 : " + (head or "(not a git work tree)"))

    if stamp and head and stamp == head:
        if _dirty():
            print(
                "STALE: stamp matches HEAD but the working tree has uncommitted changes "
                "to tracked files — the graph does not describe what is on disk."
            )
            return 1
        print("FRESH: the graph describes HEAD. Answers may be used as LEADS (see below).")
        return 0

    print("STALE: rebuild before trusting any answer.")
    return 1


def _derive_labels(graph, communities: dict) -> dict:
    """Name each community after the directory its members actually live in.

    DERIVED, never invented: the label is the most common ``source_file`` parent
    among the community's own nodes, so it cannot assert something the graph does
    not contain. Invented cluster names are exactly the unverifiable prose this
    repo has spent two rounds removing.
    """
    from collections import Counter

    labels = {}
    for cid, members in communities.items():
        dirs = Counter()
        for m in members:
            src = graph.nodes.get(m, {}).get("source_file")
            if src:
                dirs[str(Path(src).parent).replace("\\", "/")] += 1
        if not dirs:
            labels[cid] = f"Community {cid}"
            continue
        top, n = dirs.most_common(1)[0]
        labels[cid] = f"{top} ({n}/{len(members)})"
    return labels


def build(paths: list[str] | None = None) -> int:
    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.detect import detect
    from graphify.export import to_json
    from graphify.extract import collect_files, extract

    OUT.mkdir(exist_ok=True)

    roots = [Path(x) for x in (paths or ["."])]
    code = []
    for root in roots:
        if not root.exists():
            print(f"ERROR: no such path: {root}")
            return 1
        for f in detect(root).get("files", {}).get("code", []):
            p = Path(f)
            code.extend(collect_files(p) if p.is_dir() else [p])
    code = sorted(set(code))
    if not code:
        print("ERROR: no code files detected — refusing to write an empty graph.")
        return 1
    print(f"code files: {len(code)} (documents and images deliberately excluded)")

    ast = extract(code, cache_root=Path("."))
    print(f"AST: {len(ast['nodes'])} nodes, {len(ast['edges'])} edges")

    extraction = {
        "nodes": ast["nodes"],
        "edges": ast["edges"],
        "hyperedges": [],
        "input_tokens": 0,
        "output_tokens": 0,
    }
    graph = build_from_json(extraction, root=".", directed=True)
    if graph.number_of_nodes() == 0:
        print("ERROR: graph is empty — refusing to overwrite a good one.")
        return 1

    communities = cluster(graph)
    score_all(graph, communities)
    labels = _derive_labels(graph, communities)
    if not to_json(graph, communities, str(GRAPH), community_labels=labels):
        print(
            "ERROR: graphify refused the write (its shrink guard: the existing graph has "
            f"more nodes). If that shrink is intentional, delete {GRAPH} and re-run."
        )
        return 1

    print(
        f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges, "
        f"{len(communities)} communities -> {GRAPH}"
    )
    if graph.number_of_nodes() > 5000:
        print(
            f"\nNOTE: {graph.number_of_nodes()} nodes is above graphify's 5,000 HTML limit, so "
            "`graphify export html` will AGGREGATE to a community view -- each dot becomes a "
            "cluster, not a function. The JSON keeps full per-symbol detail either way. For a "
            "browsable node-level picture, re-run scoped, e.g.:\n"
            "  python <this-script> --path src/module_a src/module_b"
        )
    print()
    return check()


def main() -> int:
    argv = sys.argv[1:]
    if "--check" in argv:
        # Read-only staleness gate: reads graph.json and shells to git, no graphify
        # import needed. Must run BEFORE the interpreter dispatch below so it stays true
        # to its own promise (module docstring, `check()` docstring) of being safe to run
        # anywhere, on any interpreter -- including one where graphify can't be found at
        # all.
        return check()
    _reexec_with_graphify()
    paths = argv[argv.index("--path") + 1 :] if "--path" in argv else None
    return build(paths)


if __name__ == "__main__":
    raise SystemExit(main())
