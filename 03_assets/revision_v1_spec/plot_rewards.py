"""CPU-only analytical figures for a proposed Revision v1; no environment imports.

Run with numpy and matplotlib. Writes figures, sampled values, and formula checks
beside this file. These are synthetic formula comparisons, not rollout results.
"""

from pathlib import Path
import csv
import hashlib
import json
import math
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/revision_v1_mpl")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RADIUS, DT = 0.03, 0.02
OLD, NEW = "#757575", "#146c94"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def old_position(d):
    d = np.asarray(d)
    inner = 2.0 ** (-(d / RADIUS) ** 2) * (1 + np.clip(1 - d / RADIUS, 0, 1) ** 2)
    outer = 0.5 * np.clip((0.08 - d) / (0.08 - RADIUS), 0, 1) ** 2
    return np.where(d <= RADIUS, inner, outer)


def new_position(d):
    d = np.asarray(d)
    return np.where(d < RADIUS, 2 * 2.0 ** (-4 * (d / RADIUS) ** 2), 0.0)


def speed(v, new=False):
    excess = np.maximum(np.asarray(v) - (0.05 if new else 0), 0)
    return 2.0 ** (-(excess / 0.05) ** 2)


def hold(d, v, new=False):
    return 8 * (new_position(d) if new else old_position(d)) * speed(v, new)


def excess_cost(x, free, cap=100):
    ceiling = 0.5 * (math.log(cap) + math.log(2 + 1 / cap))
    return np.minimum(0.5 * np.expm1(2 * np.clip(np.asarray(x) - free, 0, ceiling)), cap)


def schedule(i, points, interval=250):
    # Exact scalar interpolation/quantization rule of current scheduled_value.
    if i <= points[0][0]:
        return points[0][1]
    for (start, first), (end, last) in zip(points, points[1:]):
        if i < end:
            elapsed = ((i - start) // interval) * interval
            return first + (last - first) * elapsed / (end - start)
    return points[-1][1]


def old_population(i):
    return (min(4, 1 + max(0, (i - 2500) // 1000 + 1)),
            min(5, 1 + max(0, (i - 2000) // 1000 + 1)))


def new_population(i):
    # Proposed interpretation: White at 10k, Gray at 12k, White at 14k.
    return (3 + int(i >= 12000), 3 + int(i >= 10000) + int(i >= 14000))


def save(fig, name):
    fig.savefig(OUT / (name + ".png"), dpi=160, bbox_inches="tight")
    plt.close(fig)


def decorate(ax, title, x, y):
    ax.set(title=title, xlabel=x, ylabel=y)
    ax.grid(alpha=0.22)


def make_figures():
    d = np.unique(np.r_[np.linspace(0, 0.09, 1000), RADIUS - 1e-8, RADIUS])
    v = np.linspace(0, 0.18, 1000)
    fig, axs = plt.subplots(2, 2, figsize=(11, 8), layout="constrained")
    for ax, vel in zip([axs[0, 0], axs[1, 0]], [0, 0.05]):
        ax.plot(d * 100, hold(d, vel), color=OLD, label="v0")
        ax.plot(d * 100, hold(d, vel, True), color=NEW, label="proposed v1")
        ax.axvline(3, color="black", ls=":", lw=1)
        decorate(ax, f"Hold at speed {vel * 100:g} cm/s", "XY distance (cm)", "Weighted reward rate (1/s)")
        ax.legend()
    axs[0, 1].plot(v * 100, speed(v), color=OLD, label="v0")
    axs[0, 1].plot(v * 100, speed(v, True), color=NEW, label="proposed v1")
    axs[0, 1].axvline(5, color="black", ls=":", lw=1)
    decorate(axs[0, 1], "Speed multiplier: flat through 5 cm/s", "Target 3D speed (cm/s)", "Multiplier")
    axs[0, 1].legend()
    near = d[d <= 0.031]
    axs[1, 1].plot(near * 100, hold(near, 0), color=OLD, label="v0")
    axs[1, 1].plot(near * 100, hold(near, 0, True), color=NEW, label="proposed v1")
    axs[1, 1].scatter([3], [1], facecolors="white", edgecolors=NEW, zorder=4)
    axs[1, 1].scatter([3], [0], color=NEW, zorder=4)
    decorate(axs[1, 1], "v1 center 16; inner boundary limit 1; at 3 cm: 0", "XY distance (cm)", "Weighted reward rate (1/s)")
    axs[1, 1].legend()
    fig.suptitle("Analytical comparison | valid Hold geometry | actual step reward = rate x 0.02")
    save(fig, "01_hold_curves")

    ds, vs = np.linspace(0, .08, 401), np.linspace(0, .15, 301)
    D, V = np.meshgrid(ds, vs)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    for ax, new in zip(axs, [False, True]):
        im = ax.pcolormesh(D * 100, V * 100, hold(D, V, new), cmap="viridis", vmin=0, vmax=16, shading="auto")
        ax.axvline(3, color="white", ls=":", lw=1)
        ax.axhline(5, color="white", ls=":", lw=1)
        ax.set(title="proposed v1" if new else "v0", xlabel="XY distance (cm)", ylabel="Target 3D speed (cm/s)")
    fig.colorbar(im, ax=axs, label="Weighted Hold rate (1/s)")
    fig.suptitle("Same color scale | no Hold outside 3 cm in v1")
    save(fig, "02_hold_heatmaps")

    fig, axs = plt.subplots(2, 2, figsize=(11, 7.5), layout="constrained")
    angle = np.linspace(0, 1.1, 500)
    disp = np.linspace(0, .25, 500)
    accel = np.linspace(0, 26, 500)
    tilt = -30 * np.clip((angle - math.radians(5)) / (.9 - math.radians(5)), 0, 1) ** 2
    displacement = -150 * np.minimum(disp ** 2, .04)
    acceleration = -.05 * excess_cost(accel, 20)
    for ax, x, y, title, label in [
        (axs[0, 0], np.degrees(angle), tilt, "object_tilt_penalty: one active object", "Tilt angle (degrees)"),
        (axs[0, 1], disp * 100, displacement, "obstacle_displacement_penalty: one obstacle", "3D displacement from reset (cm)"),
        (axs[1, 0], accel, acceleration, "object_acceleration_penalty: one active object", "COM acceleration (m/s^2)"),
    ]:
        ax.plot(x, y, color=OLD, lw=4, alpha=.6, label="v0 component at 10k")
        ax.plot(x, y, color=NEW, ls="--", label="v1 separate term")
        decorate(ax, title, label, "Weighted penalty rate (1/s)")
        ax.legend(fontsize=8)
    q = np.linspace(0, 1, 500)
    ct = np.clip((.5*q - math.radians(5))/(.9-math.radians(5)), 0, 1)**2
    cd = np.minimum((.12*q)**2, .04)
    ca = excess_cost(23*q, 20)
    combined = -(30*(ct+5*cd)+.05*ca)
    split = -30*ct-150*cd-.05*ca
    axs[1, 1].plot(q, combined, color=OLD, lw=4, alpha=.6, label="v0 combined at 10k")
    axs[1, 1].plot(q, split, color=NEW, ls="--", label="v1 sum")
    decorate(axs[1, 1], "Synthetic joint sweep: combined == sum", "Synthetic severity (not time)", "Weighted penalty rate (1/s)")
    axs[1, 1].legend(fontsize=8)
    fig.suptitle("Splitting preserves formulas | fixed comparison at v0 iteration 10000")
    save(fig, "03_object_penalty_split")

    fig, axs = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    delta = np.linspace(0, 70, 600)
    u = np.clip((delta-20)/30, 0, 1)
    raw = np.expm1(3*u)/math.expm1(3)
    axs[0].plot(delta, -.1*raw, color=NEW, lw=2, label="v1: independent, raw cap 1")
    for budget, ls in [(0, ":"), (.0005, "--"), (.002, "-.")]:
        axs[0].plot(delta, -np.minimum(.1*raw, budget/DT), ls=ls, label=f"v0 remaining budget {budget:g}")
    decorate(axs[0], "Wrench magnitude change (moment excess = 0)", "Force magnitude change per step (N)", "Penalty rate (1/s)")
    axs[0].legend(fontsize=8)
    force = np.linspace(45, 55, 500)
    cost = -.05*excess_cost(force, 50)
    axs[1].plot(force, cost, color=OLD, lw=4, alpha=.6, label="v0 at 10k")
    axs[1].plot(force, cost, color=NEW, ls="--", label="v1 fixed from start")
    decorate(axs[1], "Obstacle contact: formula unchanged; max rate -5", "Obstacle contact resultant force (N)", "Penalty rate (1/s)")
    axs[1].legend(fontsize=8)
    fig.suptitle("The 5% cumulative positive-reward budget belongs to wrist wrench, not obstacle contact")
    save(fig, "04_wrench_budget_and_contact")

    schedules = [
        ("Acceleration weight", [(3000, 0), (10000, -.05)], 1, -.05),
        ("Free acceleration (m/s^2)", [(3000, 50), (10000, 20)], 1, 20),
        ("Obstacle free force (N)", [(0,80),(3000,80),(6000,50),(10000,50),(12000,30)], 250, 50),
        ("Obstacle contact weight", [(0,0),(1000,0),(3000,-.02),(6000,-.05),(10000,-.05),(12000,-.1)], 250, -.05),
        ("Wrench weight", [(0,0),(1000,0),(3000,-.03),(6000,-.1)], 250, -.1),
        ("Free force change (N)", [(3000,50),(10000,20)], 250, 20),
        ("Free moment change (Nm)", [(3000,5),(10000,2)], 250, 2),
    ]
    it = np.arange(0, 16001, 10)
    fig, axs = plt.subplots(3, 3, figsize=(12, 10), layout="constrained")
    for ax, idx, title in [(axs[0,0],0,"Gray obstacles"),(axs[0,1],1,"White obstacles")]:
        ax.step(it, [old_population(i)[idx] for i in it], color=OLD, label="v0", where="post")
        ax.step(it, [new_population(i)[idx] for i in it], color=NEW, label="v1", where="post")
        decorate(ax, title, "Iteration", "Requested count"); ax.legend()
    for ax, (title, pts, interval, fixed) in zip(list(axs.flat)[2:], schedules):
        ax.plot(it, [schedule(i, pts, interval) for i in it], color=OLD, label="v0")
        ax.axhline(fixed, color=NEW, label="v1 fixed")
        ax.axvline(10000, color="black", ls=":", lw=.7)
        decorate(ax, title, "Iteration", "Value"); ax.legend(fontsize=8)
        assert schedule(10000, pts, interval) == fixed
    fig.suptitle("Proposed count schedule: (3,3) -> 10k (3,4) -> 12k (4,4) -> 14k (4,5)")
    save(fig, "05_curricula")

    t = np.arange(0, 10.0001, DT)
    fig, axs = plt.subplots(2, 2, figsize=(11, 7), layout="constrained")
    cases = [
        ("Enter, leave, re-enter, finish inside", np.where(t < 2, .08, np.where(t < 4, .02, np.where(t < 6, .05, .01)))),
        ("Brief entry, finish outside", np.where((t>=2)&(t<2.1), .02, .08)),
        ("First entry on timeout step", np.where(t<10, .08, .02)),
        ("Never enters", np.full_like(t, .08)),
    ]
    for ax, (title, distances) in zip(axs.flat, cases):
        old = np.zeros_like(t); old[-1] = 30 if distances[-1] <= RADIUS else 0
        new = np.zeros_like(t); hits = np.flatnonzero(distances < RADIUS)
        if len(hits): new[hits[0]] += 30
        new[-1] += 40 if distances[-1] <= RADIUS else 0
        ax.step(t, np.cumsum(old), color=OLD, where="post", label="v0 cumulative event reward")
        ax.step(t, np.cumsum(new), color=NEW, where="post", label="v1 cumulative event reward")
        ax.set_xlim(0, 10.3); ax.set_ylim(-3, 75)
        decorate(ax, title, "Synthetic episode time (s)", "Cumulative bonus (not a rate)")
        ax.legend(fontsize=8)
    fig.suptitle("Entry +30 once, timeout +40 once | no speed/height gate on these events")
    save(fig, "06_event_bonuses")


def validate_and_export():
    d, v = np.meshgrid(np.linspace(0, .2, 1001), np.linspace(0, 2, 1001))
    values = hold(d, v, True)
    assert np.isfinite(values).all() and values.min() >= 0 and values.max() <= 16
    assert hold(0, 0, True) == 16 and hold(.03, 0, True) == 0
    assert np.all(values[d >= .03] == 0)
    assert np.all(speed(np.linspace(0,.05,100), True) == 1)
    assert speed(.1, True) == .5 and speed(.15, True) < .063
    assert np.all(np.diff(new_position(np.linspace(0,.03,1001))) <= 0)
    assert math.isclose(float(hold(np.nextafter(.03,0),0,True)), 1, rel_tol=1e-10)
    rng = np.random.default_rng(42)
    n, count = 10000, 10
    active = rng.random((n,count)) > .2; active[:,0] = True
    theta = rng.uniform(0,1.2,(n,count)); delta = rng.normal(0,.05,(n,count,3)); accel = rng.uniform(0,30,(n,count))
    tilt = np.where(active, np.clip((theta-math.radians(5))/(.9-math.radians(5)),0,1)**2,0).sum(-1)
    mask = active.copy(); mask[:,0] = False
    disp = np.minimum(np.where(mask,np.sum(delta**2,-1),0).sum(-1),.04)
    acc = np.where(active,excess_cost(accel,20),0).sum(-1)
    legacy = -(30*(tilt+5*disp)+.05*acc)
    split = -30*tilt-150*disp-.05*acc
    err = float(np.max(np.abs(legacy-split)))
    assert np.allclose(legacy,split,atol=1e-12,rtol=1e-12)
    assert all(new_population(i)==want for i,want in [(0,(3,3)),(9999,(3,3)),(10000,(3,4)),(11999,(3,4)),(12000,(4,4)),(13999,(4,4)),(14000,(4,5)),(90000,(4,5))])
    with (OUT/'hold_samples.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['distance_cm','speed_cm_s','v0_weighted_rate','v1_weighted_rate'])
        for distance in [0,.005,.01,.015,.02,.025,.029,.03,.04,.06,.08]:
            for vel in [0,.025,.05,.075,.1,.15]:
                w.writerow([distance*100,vel*100,float(hold(distance,vel)),float(hold(distance,vel,True))])
    sources=['mdp/rewards/revision.py','mdp/reward_functions/revision.py','mdp/reward_functions/final.py',
             'mdp/reward_functions/contact_sweep_clutter_fusion.py','mdp/curricula/revision.py',
             'mdp/common/revision_layout.py','envs/revision_envs.py','assets/revision_spawners.py']
    package=ROOT/'src/inspire_sweep_baseline/inspire_sweep_baseline'
    checks={'scope':'analytical plots only; no environment execution', 'hold_bounds':[float(values.min()),float(values.max())],
            'object_split_random_cases':n,'object_split_max_abs_error':err,'count_boundary_checks':8,
            'hold_inner_boundary_limit':float(hold(np.nextafter(.03,0),0,True)),
            'source_sha256':{p:hashlib.sha256((package/p).read_bytes()).hexdigest() for p in sources}}
    (OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps({k:v for k,v in checks.items() if k!='source_sha256'},indent=2))


if __name__ == '__main__':
    validate_and_export()
    make_figures()
    print(f'Wrote six PNG figures and numerical evidence to {OUT}')
