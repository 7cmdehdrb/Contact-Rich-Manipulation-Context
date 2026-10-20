"""Compare a v3 smoke run and Contact Sweep smoke run; requires torch and PyYAML."""
import argparse
import json
from pathlib import Path
import torch
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('reference_run', type=Path)
parser.add_argument('contact_run', type=Path)
args = parser.parse_args()

def read(run, name):
    return yaml.load((run / 'params' / name).read_text(), Loader=yaml.BaseLoader)

reference, contact = [read(p, 'env.yaml') for p in (args.reference_run, args.contact_run)]
reference.pop('log_dir')
contact.pop('log_dir')
assert reference == contact, 'Environment configuration differs'
for key in ['rewards', 'events', 'terminations']:
    assert list(reference[key]) == list(contact[key]), f'{key} evaluation order differs'
assert list(reference['observations']['policy']) == list(contact['observations']['policy']), 'Observation order differs'
a, b = [read(p, 'agent.yaml') for p in (args.reference_run, args.contact_run)]
for key in ['experiment_name', 'run_name']:
    a.pop(key)
    b.pop(key)
assert a == b, 'PPO configuration differs'
a, b = [torch.load(p / 'model_0.pt', map_location='cpu', weights_only=False) for p in (args.reference_run, args.contact_run)]
models = {}
for key in ['actor_state_dict', 'critic_state_dict']:
    assert a[key].keys() == b[key].keys()
    assert all(torch.equal(x, b[key][k]) for k, x in a[key].items()), key
    models[key] = {'all_tensors_exactly_equal': True, 'tensor_count': len(a[key])}
print(json.dumps({'reference_run': str(args.reference_run), 'contact_run': str(args.contact_run),
                  'env_equal_except_log_dir': True, 'manager_and_observation_order_equal': True,
                  'ppo_equal_except_experiment_and_run_name': True, 'models_after_one_iteration': models}, indent=2))
