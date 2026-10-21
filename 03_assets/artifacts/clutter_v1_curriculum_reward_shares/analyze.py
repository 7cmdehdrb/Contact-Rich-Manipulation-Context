"""Read-only TensorBoard reward share analysis; writes only to --output-dir."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

p = argparse.ArgumentParser()
p.add_argument('--log-dir', type=Path, required=True)
p.add_argument('--output-dir', type=Path, required=True)
args = p.parse_args()
a = EventAccumulator(str(args.log_dir), size_guidance={'scalars': 0}, purge_orphaned_data=False).Reload()
tags = sorted(t for t in a.Tags()['scalars'] if t.startswith('Episode_Reward/'))
series = {t.split('/', 1)[1]: a.Scalars(t) for t in tags}
steps = [e.step for e in next(iter(series.values()))]
assert steps == sorted(set(steps))
for events in series.values():
    assert [e.step for e in events] == steps
    assert all(math.isfinite(e.value) for e in events)
assert all(y == x + 1 for x, y in zip(steps, steps[1:]))

def window(lo, hi):
    selected = [i for i,s in enumerate(steps) if lo <= s <= hi]
    means = {k: math.fsum(es[i].value for i in selected) / len(selected) for k,es in series.items()}
    positive = math.fsum(max(v,0) for v in means.values())
    negative = math.fsum(min(v,0) for v in means.values())
    absolute = positive - negative
    net = positive + negative
    rows = [{'term':k, 'mean':v, 'share_absolute_pct':abs(v)/absolute*100,
             'share_positive_pct': v/positive*100 if v >= 0 else None,
             'share_penalty_pct': v/negative*100 if v < 0 else None,
             'share_net_pct':v/net*100} for k,v in means.items()]
    extra = {}
    for tag in a.Tags()['scalars']:
        if tag.startswith('Curriculum/') or tag in ('Train/mean_reward','Train/mean_episode_length'):
            es = [e.value for e in a.Scalars(tag) if lo <= e.step <= hi]
            if es: extra[tag] = {'mean':math.fsum(es)/len(es),'min':min(es),'max':max(es)}
    return {'first':steps[selected[0]], 'last':steps[selected[-1]], 'n':len(selected),
            'positive':positive,'negative':negative,'net':net,'absolute':absolute,
            'penalty_of_positive_pct':-negative/positive*100,'rows':rows,'extra':extra}

main = window(12000,steps[-1])
report = {'source':str(args.log_dir), 'source_files':[
    {'name':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
    for f in sorted(args.log_dir.glob('events.out.tfevents.*'))],
    'validation':'15 aligned finite scalar series; unique consecutive steps.',
    'available':{'first':steps[0],'last':steps[-1],'n':len(steps)},
    'main':main,
    'windows':[window(lo,min(hi,steps[-1])) for lo,hi in [(11000,11999),(12000,12399),(12400,steps[-1])]]}
args.output_dir.mkdir(parents=True,exist_ok=True)
(args.output_dir/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
with (args.output_dir/'reward_shares.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(main['rows'][0]));w.writeheader();w.writerows(main['rows'])
print(json.dumps(report,ensure_ascii=False,indent=2))
