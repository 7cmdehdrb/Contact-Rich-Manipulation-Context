"""Plot exactly one reward per invocation, with no subplots.

Install: pip install numpy matplotlib
Run: python plot_reward_individual.py goal
     python plot_reward_individual.py normal
     python plot_reward_individual.py contact
     python plot_reward_individual.py time
Save: python plot_reward_individual.py goal --save goal_reward.png

Parameters below illustrate the proposed, unweighted reward terms.
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt


def make_axes(title, xlabel):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_title(title, fontsize=15, pad=12)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("Reward", fontsize=12)
    ax.grid(True, alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def plot_goal(sigma_p=0.10):
    """sigma_p and distance are in meters; sigma_p must be positive."""
    if sigma_p <= 0:
        raise ValueError("sigma_p must be positive")
    distance = np.linspace(0.0, 0.30, 500)
    reward = np.exp(-distance / sigma_p)
    fig, ax = make_axes("Goal reward", "Target-goal distance (m)")
    ax.plot(distance, reward, color="tab:blue", linewidth=2.5)
    ax.set_xlim(0, 0.30)
    ax.set_ylim(-0.03, 1.03)
    ax.text(0.98, 0.95, rf"$\sigma_p={sigma_p:g}\ \mathrm{{m}}$",
            transform=ax.transAxes, ha="right", va="top")
    fig.tight_layout()
    return fig


def plot_normal():
    """Zero for aligned normals, -1 for opposite directions."""
    angle_deg = np.linspace(0.0, 180.0, 500)
    reward = -(1.0 - np.cos(np.deg2rad(angle_deg))) / 2.0
    fig, ax = make_axes("Contact-normal reward", "Normal-sweep angle (deg)")
    ax.plot(angle_deg, reward, color="tab:purple", linewidth=2.5)
    ax.set_xlim(0, 180)
    ax.set_xticks(np.arange(0, 181, 30))
    ax.set_ylim(-1.03, 0.03)
    fig.tight_layout()
    return fig


def plot_contact(beta=0.5):
    """Assume alpha_i = 1 for all 17 regions; exclude the side header."""
    if not 0 <= beta <= 1:
        raise ValueError("beta must be in [0, 1]")
    count = np.arange(18)  # 0, 1, ..., 17
    contact_present = (count > 0).astype(float)
    active_fraction = count / 17.0
    reward = beta * contact_present + (1.0 - beta) * active_fraction - 1.0
    fig, ax = make_axes("Contact reward", "Number of active contact regions")
    # Markers only: contact count is discrete.
    ax.scatter(count, reward, color="tab:green", s=50, zorder=3)
    ax.set_xticks(count)
    ax.set_xlim(-0.5, 17.5)
    ax.set_ylim(-1.03, 0.03)
    ax.text(0.98, 0.10, rf"$\beta={beta:g},\quad\alpha_i=1$",
            transform=ax.transAxes, ha="right", va="bottom")
    fig.tight_layout()
    return fig


def plot_time(dt=0.02, t_ref=10.0, show_cumulative=True):
    """Per-step reward is constant; cumulative reward is undiscounted."""
    if dt <= 0 or t_ref <= 0:
        raise ValueError("dt and t_ref must be positive")
    elapsed = np.arange(int(np.ceil(t_ref / dt)) + 1) * dt
    step_reward = np.full_like(elapsed, -dt / t_ref)
    fig, ax = make_axes("Time reward", "Elapsed time (s)")
    ax.plot(elapsed, step_reward, color="tab:orange", linewidth=2.5,
            label=f"Per step: {-dt / t_ref:g}")
    if show_cumulative:
        ax.plot(elapsed, -elapsed / t_ref, "--", color="slategray", linewidth=2,
                label="Cumulative (undiscounted)")
        ax.set_ylim(-1.05, 0.05)
    ax.set_xlim(0, t_ref)
    ax.legend()
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display one reward graph.")
    parser.add_argument("reward", choices=["goal", "normal", "contact", "time"])
    parser.add_argument("--save", metavar="PATH", help="Save instead of opening a window.")
    args = parser.parse_args()
    functions = {"goal": plot_goal, "normal": plot_normal,
                 "contact": plot_contact, "time": plot_time}
    figure = functions[args.reward]()
    if args.save:
        figure.savefig(args.save, dpi=300, bbox_inches="tight")
        plt.close(figure)
    else:
        plt.show()
