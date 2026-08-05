#!/usr/bin/env python3
"""ssj_solve.py -- standardized driver for sequence-space-Jacobian (SSJ) models.

Wraps the official `sequence-jacobian` package (Auclert, Bardoczy, Rognlie,
Straub 2021). You supply the *economics* -- a model module defining the het block,
the simple blocks, and the calibration -- and this driver runs the boilerplate
linear-algebra pipeline that is infeasible by hand:

    load module -> steady state -> GE Jacobians -> determinacy -> IRFs -> plots

USAGE
    python ssj_solve.py <model_module.py> [options]

The model module must expose a function `dag()` returning a dict:
    {
      "model":   CombinedBlock,        # dynamic model (Jacobians / IRFs)
      "ss":      SteadyStateDict,      # already-solved steady state
      "unknowns": [str, ...],          # GE unknown paths (e.g. ["K"])
      "targets":  [str, ...],          # GE equilibrium conditions (e.g. ["asset_mkt"])
      "inputs":   [str, ...],          # exogenous shocks (e.g. ["Z"])
      "report_outputs": [str, ...],    # (optional) outputs to print/plot
      "shocks":   {name: {"rho": float, "size": float}},  # (optional) AR(1) shocks
    }
Build the steady state inside dag() (typically via a separate SS-inverted model)
and return only the solved `ss`; the driver consumes `ss`, not the SS model.
See example_asset_pricing.py for a worked finance example.

IMPORTANT: sequence-jacobian discovers each block's outputs via
inspect.getsource(), so model blocks must be defined in a real .py file (this
driver imports your module from disk -- that satisfies the requirement). Blocks
defined in a REPL/stdin/exec context fail with "could not get source code".

OPTIONS
    --T N            truncation horizon for Jacobians/IRFs (default 300)
    --shock NAME     which input to shock (default: first in "shocks", else first input)
    --rho R          AR(1) persistence of the shock (overrides module default)
    --size S         shock size at t=0 (overrides module default)
    --out DIR        output directory for plots + IRF csv (default output/ssj)
    --no-plot        skip PNG generation (still writes the IRF csv)
    --skip-determinacy  skip the winding-number determinacy check
"""
import argparse
import importlib.util
import os
import sys

import numpy as np


# ----------------------------------------------------------------------------
# Determinacy: winding-number criterion (Onatski 2006; Auclert et al. 2021 App.).
# ----------------------------------------------------------------------------
def winding_number_determinacy(H_U, n_unknowns, n_targets, T, n_points=4096):
    """Best-effort determinacy check from the GE Jacobian H_U (= dTargets/dUnknowns).

    The sequence-space system is determinate iff the winding number of
    det A(lambda) around the unit circle is zero, where A(lambda) is the symbol
    of the (asymptotically) Toeplitz Jacobian H_U. We recover the symbol from the
    central block-diagonals of H_U and count sign-consistent encirclements of the
    origin by det A(e^{i*theta}) as theta runs over [0, 2*pi).

    ASSUMPTIONS / LIMITATIONS (documented, not hidden):
      - Square system (n_unknowns == n_targets). Returns None otherwise.
      - H_U is asymptotically Toeplitz: its diagonals settle away from the t=0
        and t=T boundaries. True for SSJ models in the interior; near a
        determinacy *boundary* the truncation makes the count fragile -- corroborate
        with the solve_jacobian success below and, for a definitive answer on a
        knife-edge model, the hand calculation in Auclert et al. (2021, App. B).
      - Uses the central row block of H_U as the Toeplitz generator; needs T large
        enough that the diagonals have converged (warns if T < 50).
    Returns (winding_number:int, determinate:bool) or None if not applicable.
    """
    if n_unknowns != n_targets:
        return None
    n = n_unknowns
    if T < 50:
        print(f"  [determinacy] WARNING: T={T} is small; winding count may be unreliable.")

    # H_U is (n_targets*T) x (n_unknowns*T), laid out block by block: the (i,j)
    # block H_U[i*T:(i+1)*T, j*T:(j+1)*T] is the Jacobian of target i wrt unknown j.
    # Each block is approximately Toeplitz; read its diagonals from the central row.
    mid = T // 2
    # symbol coefficients J_k (k from -(T-1)..(T-1)) as n x n matrices.
    kmax = mid  # only trust diagonals within reach of the central row
    Jk = {k: np.zeros((n, n)) for k in range(-kmax, kmax + 1)}
    for i in range(n):
        for j in range(n):
            block = H_U[i * T:(i + 1) * T, j * T:(j + 1) * T]
            row = block[mid, :]              # entries block[mid, mid+k] ~ J_k[i,j]
            for k in range(-kmax, kmax + 1):
                col = mid + k
                if 0 <= col < T:
                    Jk[k][i, j] = row[col]

    thetas = np.linspace(0.0, 2.0 * np.pi, n_points, endpoint=False)
    det_vals = np.empty(n_points, dtype=complex)
    for idx, th in enumerate(thetas):
        z = np.exp(1j * th)
        A = np.zeros((n, n), dtype=complex)
        for k in range(-kmax, kmax + 1):
            A += Jk[k] * (z ** k)
        det_vals[idx] = np.linalg.det(A)

    # winding number = net change in arg(det) over the closed loop, / 2pi.
    closed = np.unwrap(np.angle(np.append(det_vals, det_vals[0])))
    winding = int(round((closed[-1] - closed[0]) / (2.0 * np.pi)))
    return winding, (winding == 0)


def main():
    ap = argparse.ArgumentParser(description="SSJ solver driver")
    ap.add_argument("model_module", help="path to model .py exposing dag()")
    ap.add_argument("--T", type=int, default=300)
    ap.add_argument("--shock", default=None)
    ap.add_argument("--rho", type=float, default=None)
    ap.add_argument("--size", type=float, default=None)
    ap.add_argument("--out", default="output/ssj")
    ap.add_argument("--no-plot", action="store_true")
    ap.add_argument("--skip-determinacy", action="store_true")
    args = ap.parse_args()

    # --- load the model module from disk ---
    path = os.path.abspath(args.model_module)
    if not os.path.exists(path):
        sys.exit(f"model module not found: {path}")
    spec = importlib.util.spec_from_file_location("ssj_model", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ssj_model"] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "dag"):
        sys.exit("model module must expose a dag() function (see ssj_solve.py header)")

    print(f"[1/5] Building model and solving steady state from {os.path.basename(path)} ...")
    spec_dict = mod.dag()
    model = spec_dict["model"]
    ss = spec_dict["ss"]
    unknowns = spec_dict["unknowns"]
    targets = spec_dict["targets"]
    inputs = spec_dict["inputs"]
    report_outputs = spec_dict.get("report_outputs", list(model.outputs)[:6])
    shocks_cfg = spec_dict.get("shocks", {})

    print(f"      unknowns={unknowns}  targets={targets}  inputs={inputs}")
    print("      steady-state values:")
    for k in report_outputs:
        if k in ss:
            print(f"        {k:>10} = {float(ss[k]):.6g}")

    # --- GE Jacobians ---
    print(f"[2/5] Computing general-equilibrium Jacobians (T={args.T}) ...")
    G = model.solve_jacobian(ss, unknowns, targets, inputs, outputs=report_outputs, T=args.T)
    print(f"      got GE Jacobian map G[output][input] for outputs={report_outputs}")

    # --- determinacy (winding number of det H_U) ---
    if not args.skip_determinacy:
        print("[3/5] Determinacy check (winding-number criterion) ...")
        # H_U = Jacobian of targets wrt unknowns, packed to a (n_t*T) x (n_u*T) matrix.
        try:
            H_U = model.jacobian(ss, inputs=unknowns, outputs=targets, T=args.T)
            H_U_mat = H_U.pack(args.T)
        except Exception as e:  # noqa: BLE001
            print(f"      determinacy: could not build H_U ({e}); "
                  "solve_jacobian above succeeded, so H_U is at least invertible.")
            H_U_mat = None
        if H_U_mat is not None:
            res = winding_number_determinacy(H_U_mat, len(unknowns), len(targets), args.T)
            if res is None:
                print("      determinacy: non-square system; winding check skipped "
                      "(solve_jacobian success implies a locally unique solution).")
            else:
                wn, det_ok = res
                verdict = "DETERMINATE" if det_ok else f"INDETERMINATE/NON-EXISTENT (winding={wn})"
                print(f"      determinacy verdict: {verdict}")
    else:
        print("[3/5] Determinacy check skipped (--skip-determinacy).")

    # --- IRFs ---
    print("[4/5] Solving impulse responses ...")
    shock_name = args.shock or (next(iter(shocks_cfg)) if shocks_cfg else inputs[0])
    cfg = shocks_cfg.get(shock_name, {})
    rho = args.rho if args.rho is not None else cfg.get("rho", 0.8)
    size = args.size if args.size is not None else cfg.get("size", 0.01)
    dZ = size * rho ** np.arange(args.T)
    print(f"      shock={shock_name}  AR(1) rho={rho}  size={size}")
    irfs = {o: G[o][shock_name] @ dZ for o in report_outputs if o in G and shock_name in G[o]}
    if not irfs:
        print(f"      WARNING: none of report_outputs={report_outputs} are in the GE "
              f"Jacobian for shock '{shock_name}'. Check the names match model outputs.")

    # --- write outputs ---
    os.makedirs(args.out, exist_ok=True)
    csv_path = os.path.join(args.out, "irf.csv")
    cols = list(irfs.keys())
    arr = np.column_stack([irfs[c] for c in cols]) if cols else np.empty((args.T, 0))
    header = ",".join(["t"] + cols)
    with open(csv_path, "w") as fh:
        fh.write(header + "\n")
        for t in range(args.T):
            fh.write(",".join([str(t)] + [f"{arr[t, j]:.8g}" for j in range(len(cols))]) + "\n")
    print(f"[5/5] Wrote IRFs to {csv_path}")

    if not args.no_plot and cols:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            ncol = min(len(cols), 3)
            nrow = int(np.ceil(len(cols) / ncol))
            fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3 * nrow), squeeze=False)
            horizon = min(args.T, 50)
            for i, c in enumerate(cols):
                ax = axes[i // ncol][i % ncol]
                ax.plot(np.arange(horizon), irfs[c][:horizon])
                ax.axhline(0, color="k", lw=0.5)
                ax.set_title(f"{c} response to {shock_name}")
                ax.set_xlabel("quarters")
            for j in range(len(cols), nrow * ncol):
                axes[j // ncol][j % ncol].axis("off")
            fig.tight_layout()
            png = os.path.join(args.out, "irf.png")
            fig.savefig(png, dpi=110)
            print(f"      Wrote plot to {png}")
        except Exception as e:  # noqa: BLE001
            print(f"      (plotting skipped: {e})")


if __name__ == "__main__":
    main()
