# Relative-IK-v0_1: disable first-entry bonus

## Request and final contract

Create a direct IK-v0 child disabling only `target_goal_first_entry_bonus`. Baseline commit: `2b88fe8`; existing workspace changes preserved.

- Task: `Inspire-Wrench-Refactor-Relative-IK-v0_1`.
- EnvCfg: `WrenchRefactorRelativeIKV0_1EnvCfg`, directly inherits `WrenchRefactorRelativeIKV0EnvCfg`.
- Runtime: unchanged `WrenchRefactorEnv`.
- Only environment difference: `rewards.target_goal_first_entry_bonus`, previously weight10, is now `None`.
- PPO: `WrenchRefactorRelativeIKV0_1PPORunnerCfg` directly inherits the IK-v0 runner. Only experiment_name changes to `inspire_wrench_refactor_relative_ik_v0_1`.

Scene, Command, Event/IK reset, Observation, Action, all other Rewards, Terminations and Curriculum are inherited unchanged. Contact, Hold, success bonus, 3-second success termination, symmetric initial-object observations, EEF height gating and both IK bounding boxes remain. Existing IK-v0/v1 code is unchanged.

## Validation

Extended the existing complete-config comparison to check the child against the entire parent dictionary with only the requested reward removed. Parent recreation remains unchanged. Existing inheritance and Refactor regression checks: **86 passed in 10.76s**.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_wrench_refactor.py -q --disable-warnings
```

GPU smoke and training were not run for this single configuration change. Static configuration checks do not establish policy performance.

## Training

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-IK-v0_1 --num_envs 2048 --headless
```
