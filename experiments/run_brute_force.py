"""Run brute-force DkS on small graphs and measure runtime scaling.

Usage (from the repo root):
    python3 experiments/run_brute_force.py              # both parts, n up to 24
    python3 experiments/run_brute_force.py --max-n 20   # faster scaling sweep

Outputs (in results/):
    brute_force_small_graphs.csv   optimum for every k on Dataset/graphs-1.json
    brute_force_scaling.csv        runtime vs n on G(n, p)
    brute_force_scaling.png        log-scale runtime plot
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dks import brute_force, gnp, load_json_graphs  # noqa: E402

RESULTS = ROOT / "results"
SMALL_GRAPHS = ROOT / "Dataset" / "graphs-1.json"


def timed(g, k, min_total=0.2):
    """Run brute_force, repeating fast runs so the timing isn't noise. Returns (result, seconds/run)."""
    runs, start = 0, time.perf_counter()
    while True:
        r = brute_force(g, k)
        runs += 1
        elapsed = time.perf_counter() - start
        if elapsed >= min_total or runs >= 50:
            return r, elapsed / runs


def small_graphs() -> None:
    if not SMALL_GRAPHS.exists():
        print(f"skip: {SMALL_GRAPHS} not found")
        return
    graphs = load_json_graphs(SMALL_GRAPHS)
    rows = []
    for g in graphs:
        for k in range(1, g.n + 1):
            r, secs = timed(g, k, min_total=0.01)
            rows.append({
                "graph": g.name, "n": g.n, "m": g.m, "k": k, "edges": r.edges,
                "density": round(r.edges / comb(k, 2), 4) if k > 1 else "",
                "vertices": " ".join(map(str, r.vertices)),
                "subsets": r.subsets_checked, "seconds": f"{secs:.6f}",
            })
    _write_csv(RESULTS / "brute_force_small_graphs.csv", rows)

    ks = sorted({row["k"] for row in rows})
    print("\nOptimal edges in the densest k-subgraph (Dataset/graphs-1.json)")
    print(f"{'graph':>5} {'n':>3} {'m':>3} | " + " ".join(f"k={k:<3}" for k in ks))
    for g in graphs:
        best = {row["k"]: row["edges"] for row in rows if row["graph"] == g.name}
        print(f"{g.name:>5} {g.n:>3} {g.m:>3} | " + " ".join(f"{best.get(k, ''):<5}" for k in ks))


def scaling(max_n: int, p: float, seed: int) -> None:
    rows = []
    print(f"\nRuntime scaling on G(n, {p})")
    print(f"{'n':>3} {'k':>3} {'C(n,k)':>12} {'seconds':>10} {'us/subset':>10}")
    for label, k_of in (("n/2", lambda n: n // 2), ("n/4", lambda n: n // 4)):
        for n in range(8, max_n + 1, 2):
            k = k_of(n)
            g = gnp(n, p, seed=seed + n)
            r, secs = timed(g, k)
            us = secs / r.subsets_checked * 1e6
            rows.append({"k_rule": label, "n": n, "k": k, "p": p, "subsets": r.subsets_checked,
                         "edges": r.edges, "seconds": f"{secs:.6f}", "us_per_subset": f"{us:.3f}"})
            print(f"{n:>3} {k:>3} {r.subsets_checked:>12,} {secs:>10.4f} {us:>10.3f}")
    _write_csv(RESULTS / "brute_force_scaling.csv", rows)
    _plot(rows, p)


def _plot(rows, p) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, muted, grid, axis = "#0b0b0b", "#898781", "#e1e0d9", "#c3c2b7"
    colors = {"n/2": "#2a78d6", "n/4": "#eb6834"}

    fig, ax = plt.subplots(figsize=(6, 3.6), dpi=200)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    for label, color in colors.items():
        pts = [(r["n"], float(r["seconds"])) for r in rows if r["k_rule"] == label]
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=2, marker="o", ms=5,
                markeredgecolor="#fcfcfb", markeredgewidth=1.5, label=f"k = {label}")
        ax.annotate(f"k = {label}", (xs[-1], ys[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=8, color=ink)
    ax.set_yscale("log")
    ax.set_xlabel("Number of vertices n", color=muted, fontsize=9)
    ax.set_ylabel("Runtime (seconds, log scale)", color=muted, fontsize=9)
    ax.set_title(f"Brute-force DkS runtime on G(n, {p})", color=ink, fontsize=10, loc="left")
    ax.grid(True, which="major", color=grid, lw=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(axis)
    ax.tick_params(which="both", colors=muted, labelsize=8)
    ax.set_xticks(sorted({r["n"] for r in rows}))
    ax.legend(frameon=False, fontsize=8, labelcolor=ink, loc="upper left")
    ax.margins(x=0.08)
    fig.tight_layout()
    out = RESULTS / "brute_force_scaling.png"
    fig.savefig(out, facecolor=fig.get_facecolor())
    print(f"wrote {out.relative_to(ROOT)}")


def _write_csv(path: Path, rows) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-n", type=int, default=24)
    ap.add_argument("--p", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--skip-small", action="store_true")
    ap.add_argument("--skip-scaling", action="store_true")
    args = ap.parse_args()
    if not args.skip_small:
        small_graphs()
    if not args.skip_scaling:
        scaling(args.max_n, args.p, args.seed)


if __name__ == "__main__":
    main()
