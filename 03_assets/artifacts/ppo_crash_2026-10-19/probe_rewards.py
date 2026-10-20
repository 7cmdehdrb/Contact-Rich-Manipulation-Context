"""Synthetic CPU fault injection, not a replay of either failed training run."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import pytest
import torch

p = Path('src/inspire_sweep_baseline/tests/conftest.py')
spec = importlib.util.spec_from_file_location('audit_harness', p)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
mp = pytest.MonkeyPatch()
g = h.load_mdp.__wrapped__(mp, h.tensor_math.__wrapped__())
load = next(g)
try:
    dex = load('dex_rewards')
    make = h.make_env.__wrapped__()
    for reset_distance in [0.6, 1e10]:
        env = make(1)
        env.step_dt = 0.02
        pos = env.scene['object_collection'].data.object_pos_w[:, 0]
        ref = env.scene['ee_frame'].data.target_pos_w[:, 0]
        ref[:] = pos
        ref[:, 0] += reset_distance
        reach = dex.DexReachProgress(SimpleNamespace(params={'near_radius': 0.1, 'frame_name': 'ee_frame'}), env)
        ref[:] = pos  # Return to normal position after reset snapshot.
        print('reset distance', reset_distance, 'weighted reaching reward', (reach(env) * 30 * env.step_dt).item())
    # Healthy reset snapshot: even enormous subsequent object position does not pay progress.
    env = make(1)
    env.step_dt = 0.02
    goal = dex.DexPlanarGoalProgress(SimpleNamespace(params={}), env)
    env.scene['object_collection'].data.object_pos_w[:, 0, 0] = 1e20
    print('normal goal reset, huge later position, weighted reward', (goal(env) * 300 * env.step_dt).item())
    # Finite env reward can become NaN inside PPO, after check_nan has already run.
    reward = torch.tensor([1.0])
    value = torch.tensor([float('inf')])
    timeout = torch.tensor([False])
    print('PPO timeout arithmetic with inf critic and timeout=False:', (reward + .98 * value * timeout).item())
finally:
    try:
        next(g)
    except StopIteration:
        pass
    mp.undo()
