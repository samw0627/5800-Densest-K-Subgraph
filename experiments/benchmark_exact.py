"""Benchmark the three exact DkS algorithms with k = n/2 and a 60-second limit.

Methods
    naive        itertools.combinations, recount edges of every subset   Θ(C(n,k)·k)
    incremental  DFS over subsets with a running edge count              Θ(C(n,k))
    bnb          incremental DFS + upper-bound pruning, greedy seed      exact, prunes

Graphs (all from Dataset/, instance 1 of each family)
    n = 10, 12, ..., 38  first n vertices of the 40-vertex graph PB1_d{025,05,075}.txt
                         (the induced subgraph keeps the same edge density)
    n = 40               PB1_d*.txt in full
    n = 42, 44, ..., 78  first n vertices of the 80-vertex graph ALEA1n80_d*_method2.txt
    n = 80, 100          ALEA1n{n}_d*_method2.txt
    n = 120, 140, 160    PB1_n{n}_d*.txt

The exhaustive methods do the same work at every density, so they run on the
50% graphs only. bnb runs on 25%, 50% and 75%.

A run is "infeasible" if it does not finish within --limit seconds (default 60).
Each run happens in its own process and is killed at the limit. Once a method
is infeasible at some n, larger n are skipped for that method and density.

Usage (from the repo root):
    python3 experiments/benchmark_exact.py              # full benchmark
    python3 experiments/benchmark_exact.py --limit 5    # quick smoke run
    python3 experiments/benchmark_exact.py --plot-only  # redraw from the CSV

Outputs (results/):
    exact_benchmark.csv
    exact_benchmark_runtime.png     runtime vs n, one line per method (50% density)
    exact_benchmark_bnb_density.png branch and bound at each density
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing as mp
import sys
import time
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dks import Graph, branch_and_bound, brute_force, brute_force_naive, load_kcluster  # noqa: E402

DATASET = ROOT / "Dataset"
RESULTS = ROOT / "results"
CSV_PATH = RESULTS / "exact_benchmark.csv"

METHODS = {
    "naive": brute_force_naive,
    "incremental": brute_force,
    "bnb": branch_and_bound,
}
LABELS = {
    "naive": "Naive (itertools)",
    "incremental": "Incremental count",
    "bnb": "Branch and bound",
}
# density label -> (code in n<=100 filenames, code in n>=120 filenames)
DENSITIES = {"25%": ("d025", "d025"), "50%": ("d05", "d050"), "75%": ("d075", "d075")}


# --------------------------------------------------------------------------- #
# Graph schedule
# --------------------------------------------------------------------------- #

def graph_schedule(density: str):
    """Yield (n, source_description, Graph) in increasing n."""
    small, large = DENSITIES[density]
    base = load_kcluster(DATASET / f"PB1_{small}.txt")
    for n in range(10, 40, 2):
        sub = Graph(n, [(u, v) for u, v in base.edges if v < n], name=f"{base.name}[:{n}]")
        yield n, f"PB1_{small}.txt first {n} vertices", sub
    yield 40, f"PB1_{small}.txt", base
    base80 = load_kcluster(DATASET / f"ALEA1n80_{small}_method2.txt")
    for n in range(42, 80, 2):
        sub = Graph(n, [(u, v) for u, v in base80.edges if v < n], name=f"{base80.name}[:{n}]")
        yield n, f"ALEA1n80_{small}_method2.txt first {n} vertices", sub
    for n in (80, 100):
        f = f"ALEA1n{n}_{small}_method2.txt"
        yield n, f, load_kcluster(DATASET / f)
    for n in (120, 140, 160):
        f = f"PB1_n{n}_{large}.txt"
        yield n, f, load_kcluster(DATASET / f)


# --------------------------------------------------------------------------- #
# Timed run in a child process
# --------------------------------------------------------------------------- #

def _child(method: str, g: Graph, k: int, out: mp.Queue) -> None:
    fn = METHODS[method]
    runs, total = 0, 0.0
    while True:
        t0 = time.perf_counter()
        r = fn(g, k)
        total += time.perf_counter() - t0
        runs += 1
        # Repeat very fast runs so the timing isn't dominated by noise.
        if total >= 0.2 or runs >= 50:
            break
    out.put({
        "seconds": total / runs,
        "edges": r.edges,
        "subsets_checked": r.subsets_checked,
        "nodes": getattr(r, "nodes", ""),
    })


def run_with_limit(method: str, g: Graph, k: int, limit: float) -> dict | None:
    """Return the child's measurements, or None if it exceeded the limit."""
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_child, args=(method, g, k, q))
    p.start()
    # Allow a little slack for process start-up; the child's own timer decides.
    p.join(limit + 5)
    if p.is_alive():
        p.terminate()
        p.join()
        return None
    try:
        res = q.get(timeout=5)
    except Exception:
        return None
    return None if res["seconds"] > limit else res


# --------------------------------------------------------------------------- #
# Benchmark
# --------------------------------------------------------------------------- #

def benchmark(limit: float) -> list[dict]:
    plan = [("naive", "50%"), ("incremental", "50%"),
            ("bnb", "25%"), ("bnb", "50%"), ("bnb", "75%")]
    rows = []
    for method, density in plan:
        print(f"\n== {LABELS[method]}, density {density}")
        print(f"{'n':>4} {'k':>3} {'status':>10} {'seconds':>10} {'edges':>6} "
              f"{'subsets checked':>16} {'C(n,k)':>22}")
        infeasible = False
        for n, source, g in graph_schedule(density):
            k = n // 2
            row = {
                "method": method, "density": density, "source": source,
                "n": n, "k": k, "m": g.m,
                "realized_density": round(g.m / comb(n, 2), 4),
                "status": "", "seconds": "", "edges": "",
                "subsets_checked": "", "nodes": "", "total_subsets": comb(n, k),
            }
            if infeasible:
                row["status"] = "skipped"
            else:
                res = run_with_limit(method, g, k, limit)
                if res is None:
                    row["status"] = "infeasible"
                    infeasible = True
                else:
                    row.update(status="ok", seconds=f"{res['seconds']:.6f}", edges=res["edges"],
                               subsets_checked=res["subsets_checked"], nodes=res["nodes"])
            rows.append(row)
            if row["status"] != "skipped":
                print(f"{n:>4} {k:>3} {row['status']:>10} {row['seconds'] or '-':>10} "
                      f"{row['edges'] if row['edges'] != '' else '-':>6} "
                      f"{row['subsets_checked'] if row['subsets_checked'] != '' else '-':>16} "
                      f"{row['total_subsets']:>22,}", flush=True)
    return rows


def check_agreement(rows: list[dict]) -> None:
    """All methods that finished on the same graph must report the same optimum."""
    by_graph: dict[tuple, set] = {}
    for r in rows:
        if r["status"] == "ok":
            by_graph.setdefault((r["density"], r["n"]), set()).add(int(r["edges"]))
    bad = {key: vals for key, vals in by_graph.items() if len(vals) > 1}
    if bad:
        print("\nWARNING: methods disagree on the optimum:", bad)
    else:
        print(f"\nAll methods agree on the optimum for every graph they finished ({len(by_graph)} graphs).")


# --------------------------------------------------------------------------- #
# Plots
# --------------------------------------------------------------------------- #

SURFACE, INK, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#898781", "#e1e0d9", "#c3c2b7"


def _style(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_yscale("log")
    ax.set_xlabel("Number of vertices n  (k = n/2)", color=MUTED, fontsize=9)
    ax.set_ylabel("Runtime (seconds, log scale)", color=MUTED, fontsize=9)
    ax.set_title(title, color=INK, fontsize=10, loc="left")
    ax.grid(True, which="major", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.tick_params(which="both", colors=MUTED, labelsize=8)


def _series(ax, rows, color, label, limit, ha="center"):
    ok = [(r["n"], float(r["seconds"])) for r in rows if r["status"] == "ok"]
    bad = [r["n"] for r in rows if r["status"] == "infeasible"]
    if ok:
        xs, ys = zip(*ok)
        ax.plot(xs, ys, color=color, lw=2, marker="o", ms=4.5,
                markeredgecolor=SURFACE, markeredgewidth=1.2, label=label)
        if not bad:
            ax.annotate(label, (xs[-1], ys[-1]), xytext=(5, -2), textcoords="offset points",
                        va="center", fontsize=7.5, color=INK)
    if bad:
        dx = {"center": 0, "right": 3, "left": -3}[ha]
        ax.annotate(label, (bad[0], limit), xytext=(dx, 9), textcoords="offset points",
                    ha=ha, va="bottom", fontsize=7.5, color=INK)  # first infeasible n, drawn on the limit line
        ax.plot([bad[0]], [limit], marker="X", ms=8, color=color,
                markeredgecolor=SURFACE, markeredgewidth=1.2, linestyle="none")
        if ok:
            ax.plot([ok[-1][0], bad[0]], [ok[-1][1], limit], color=color, lw=1.2, ls=":")


def _label_alignment(series):
    """series: list of (key, rows). Push apart labels of × markers closer than 6 in n."""
    first_bad = {}
    for key, rows in series:
        bad = [r["n"] for r in rows if r["status"] == "infeasible"]
        if bad:
            first_bad[key] = bad[0]
    ha = {key: "center" for key, _ in series}
    ordered = sorted(first_bad, key=first_bad.get)
    for a, b in zip(ordered, ordered[1:]):
        if first_bad[b] - first_bad[a] < 6:
            ha[a], ha[b] = "right", "left"
    return ha


def _limit_line(ax, limit):
    ax.axhline(limit, color=INK, lw=1, ls="--", zorder=1)
    ax.annotate(f"{limit:g} s limit (× = first infeasible n)", (0.01, limit), xycoords=("axes fraction", "data"),
                xytext=(0, -10), textcoords="offset points", fontsize=7.5, color=INK)


def plot(rows: list[dict], limit: float) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for r in rows:
        r["n"] = int(r["n"])

    # 1) One line per method, 50% density.
    colors = {"naive": "#2a78d6", "incremental": "#eb6834", "bnb": "#1baf7a"}
    fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    _style(ax, "Exact DkS algorithms: runtime vs n (benchmark graphs, 50% density)")
    series = [(m, [r for r in rows if r["method"] == m and r["density"] == "50%"]) for m in colors]
    ha = _label_alignment(series)
    for method, sel in series:
        _series(ax, sel, colors[method], LABELS[method], limit, ha[method])
    _limit_line(ax, limit)
    ax.set_ylim(top=limit * 8)
    ns = sorted({r["n"] for r in rows if r["density"] == "50%" and r["status"] != "skipped"})
    ax.set_xticks(ns, [str(n) if n % 8 == 0 or n > 80 else "" for n in ns])
    ax.legend(frameon=False, fontsize=8, labelcolor=INK, loc="lower right")
    ax.margins(x=0.1)
    fig.tight_layout()
    fig.savefig(RESULTS / "exact_benchmark_runtime.png", facecolor=SURFACE)
    plt.close(fig)

    # 2) Branch and bound at each density (ordinal: light -> dark blue).
    shades = {"25%": "#6da7ec", "50%": "#2a78d6", "75%": "#104281"}
    fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    _style(ax, "Branch and bound: runtime vs n by edge density")
    series = [(d, [r for r in rows if r["method"] == "bnb" and r["density"] == d]) for d in shades]
    ha = _label_alignment(series)
    for density, sel in series:
        _series(ax, sel, shades[density], f"density {density}", limit, ha[density])
    _limit_line(ax, limit)
    ax.set_ylim(top=limit * 8)
    ns = sorted({r["n"] for r in rows if r["method"] == "bnb" and r["status"] != "skipped"})
    ax.set_xticks(ns, [str(n) if n % 8 == 0 or n > 80 else "" for n in ns])
    ax.legend(frameon=False, fontsize=8, labelcolor=INK, loc="lower right")
    ax.margins(x=0.1)
    fig.tight_layout()
    fig.savefig(RESULTS / "exact_benchmark_bnb_density.png", facecolor=SURFACE)
    plt.close(fig)
    print("wrote results/exact_benchmark_runtime.png, results/exact_benchmark_bnb_density.png")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=float, default=60.0, help="seconds before a run is infeasible")
    ap.add_argument("--plot-only", action="store_true")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)
    if args.plot_only:
        with CSV_PATH.open() as f:
            rows = list(csv.DictReader(f))
    else:
        rows = benchmark(args.limit)
        with CSV_PATH.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {CSV_PATH.relative_to(ROOT)}")
    check_agreement(rows)
    plot(rows, args.limit)


if __name__ == "__main__":
    main()
