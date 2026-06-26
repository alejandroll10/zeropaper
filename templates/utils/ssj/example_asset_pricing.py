"""Worked finance example: heterogeneous-agent asset pricing in sequence space.

A production economy where physical capital is the single risky asset. Households
face idiosyncratic labor-income risk, cannot insure it, and save in the capital
claim. The equilibrium return r on that claim is an *asset price*: it is pinned
down by the wealth distribution (precautionary savers bid the return down) and it
moves with aggregate risk. We trace the impulse response of the asset return r to
an aggregate-productivity (Z) shock -- the object a representative-agent asset
pricer cannot produce, because here the response is shaped by the cross-section
of wealth (the household block's general-equilibrium Jacobian).

This is the canonical Krusell-Smith incomplete-markets economy, read as an
asset-pricing model: capital = the risky asset, r = its excess return over the
(degenerate) storage benchmark, Z = aggregate risk. To go to an explicit equity
premium you would add a riskless bond in zero net supply and a second market-
clearing condition; the sequence-space workflow is identical (one more unknown,
one more target). See ssj.md, "Extending to an explicit equity premium."

The module exposes a single entry point, dag(), returning the contract the
ssj_solve.py driver consumes. Blocks MUST live in a real .py file like this one:
sequence-jacobian reads function source with inspect.getsource() to discover each
block's outputs, so blocks defined in a REPL/stdin/exec context fail.
"""

from sequence_jacobian import grids, simple, create_model, hetblocks

# Standard incomplete-markets household (CRRA, one asset, idiosyncratic income).
hh = hetblocks.hh_sim.hh


@simple
def firm(K, L, Z, alpha, delta):
    # r is the return on the risky capital claim -- the asset price we track.
    r = alpha * Z * (K(-1) / L) ** (alpha - 1) - delta
    w = (1 - alpha) * Z * (K(-1) / L) ** alpha
    Y = Z * K(-1) ** alpha * L ** (1 - alpha)
    return r, w, Y


@simple
def mkt_clearing(K, A, Y, C, delta):
    # Households' asset demand A must equal the capital stock K (asset market).
    asset_mkt = A - K
    I = K - (1 - delta) * K(-1)
    goods_mkt = Y - C - I
    return asset_mkt, goods_mkt, I


@simple
def firm_ss(r, Y, L, delta, alpha):
    """Invert the firm's FOCs at the steady state: back out (K, Z, w) from
    targets (Y, r). This leaves discount factor beta as the only steady-state
    unknown, so the SS solve is one-dimensional."""
    rk = r + delta
    K = alpha * Y / rk
    Z = Y / K ** alpha / L ** (1 - alpha)
    w = (1 - alpha) * Z * (K / L) ** alpha
    return K, Z, w


def make_grids(rho, sigma, nS, amax, nA):
    e_grid, _, Pi = grids.markov_rouwenhorst(rho=rho, sigma=sigma, N=nS)
    a_grid = grids.agrid(amax=amax, n=nA)
    return e_grid, Pi, a_grid


def income(w, e_grid):
    y = w * e_grid
    return y


def dag():
    """Build the model, solve the steady state, and return the driver contract."""
    household = hh.add_hetinputs([income, make_grids])
    model = create_model([household, firm, mkt_clearing], name="HA-asset-pricing")
    model_ss = create_model([household, firm_ss, mkt_clearing], name="HA-asset-pricing SS")

    calibration = {
        "eis": 1.0, "delta": 0.025, "alpha": 0.11,
        "rho": 0.966, "sigma": 0.5,
        "Y": 1.0, "L": 1.0, "nS": 3, "nA": 100, "amax": 200, "r": 0.01,
    }
    unknowns_ss = {"beta": (0.98 / 1.01, 0.999 / 1.01)}
    targets_ss = {"asset_mkt": 0.0}
    ss = model_ss.solve_steady_state(calibration, unknowns_ss, targets_ss, solver="brentq")

    # model_ss above is a local used only to solve the steady state; the driver
    # consumes the solved `ss`, not the SS model, so it is not a contract key.
    return {
        "model": model,            # the dynamic model (for Jacobians / IRFs)
        "ss": ss,
        "unknowns": ["K"],         # GE unknown path
        "targets": ["asset_mkt"],  # GE equilibrium condition
        "inputs": ["Z"],           # exogenous shock(s)
        # What to plot as the headline asset-pricing response:
        "report_outputs": ["r", "K", "C", "Y"],
        # Shock: AR(1) productivity innovation.
        "shocks": {"Z": {"rho": 0.8, "size": 0.01}},
    }
