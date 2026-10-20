"""Read-only TensorBoard/checkpoint audit; run with Isaac Lab's Python from workspace root."""
import csv
import json
from pathlib import Path
import torch
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

BASE = Path('logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v2')
OUT = Path(__file__).resolve().parent
RUNS = ['2026-10-19_12-16-03', '2026-10-19_17-52-20_resume_8500']
summary = {}
with (OUT / 'scalars.csv').open('w') as sf, (OUT / 'checkpoints.csv').open('w') as cf:
    sw, cw = csv.writer(sf), csv.writer(cf)
    selected = ['Loss/value', 'Loss/surrogate', 'Loss/learning_rate', 'Policy/mean_std', 'Train/mean_reward']
    sw.writerow(['run', 'iteration', *selected])
    cw.writerow(['run', 'checkpoint', 'nonfinite_tensor_paths', 'std_min', 'std_max', 'model_max_abs', 'optimizer_lr'])
    for run in RUNS:
        acc = EventAccumulator(str(BASE / run), size_guidance={'scalars': 0}).Reload()
        tags = acc.Tags()['scalars']
        values = {t: {e.step: e.value for e in acc.Scalars(t)} for t in selected}
        for step in values['Loss/value']:
            sw.writerow([run, step, *[values[t][step] for t in selected]])
        count, invalid, min_std = 0, [], float('inf')
        for p in sorted((BASE / run).glob('model_*.pt'), key=lambda p: int(p.stem.split('_')[1])):
            state = torch.load(p, map_location='cpu', weights_only=False)
            bad = []
            def walk(x, name=''):
                if torch.is_tensor(x):
                    if not torch.isfinite(x).all():
                        bad.append(name)
                elif isinstance(x, dict):
                    for k, v in x.items():
                        walk(v, name + '/' + str(k))
                elif isinstance(x, (list, tuple)):
                    for k, v in enumerate(x):
                        walk(v, name + '/' + str(k))
            walk(state)
            std = state['actor_state_dict']['distribution.std_param']
            maximum = max(float(x.abs().max()) for k in ['actor_state_dict', 'critic_state_dict'] for x in state[k].values() if torch.is_tensor(x))
            cw.writerow([run, p.name, json.dumps(bad), float(std.min()), float(std.max()), maximum, state['optimizer_state_dict']['param_groups'][0]['lr']])
            count += 1
            min_std = min(min_std, float(std.min()))
            invalid.extend(bad)
        v = acc.Scalars('Loss/value')
        summary[run] = {'scalar_tags': len(tags), 'iterations': len(v), 'first_step': v[0].step, 'last_step': v[-1].step,
                        'first_value_loss_gt_1000': next([e.step, e.value] for e in v if e.value > 1000),
                        'nonfinite_value_steps': [e.step for e in v if not torch.isfinite(torch.tensor(e.value))],
                        'checkpoint_count': count, 'nonfinite_checkpoint_tensors': invalid, 'minimum_saved_std': min_std}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
# Demonstrate that this exception does not distinguish negative std from NaN.
for s in [-1.0, float('nan')]:
    try:
        torch.normal(torch.zeros(1), torch.tensor([s]))
    except RuntimeError as e:
        print(f'std={s}: {e}')
