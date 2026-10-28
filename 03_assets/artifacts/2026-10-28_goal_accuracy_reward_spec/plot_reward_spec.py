"""Analytical specification figures only; does not import or modify environment code."""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT = Path(__file__).resolve().parent
A_EXP = 20.0

def integral(q):
    return (3*math.exp(-A_EXP*.15)
            +3*(math.exp(-A_EXP*q)-math.exp(-A_EXP*.15))/(A_EXP*(.15-q))
            +4*math.exp(-A_EXP*q))
WEIGHT = 3.7
def distance(t,q):
    return .15-(.15-q)*np.clip((t-3)/3,0,1)
def cumulative(t,q):
    start=math.exp(-A_EXP*.15)
    k=A_EXP*(.15-q)/3
    u=np.clip(t-3,0,3)
    return WEIGHT*(np.minimum(t,3)*start+start*np.expm1(k*u)/k+np.maximum(t-6,0)*math.exp(-A_EXP*q))
plt.rcParams.update({'font.size':10,'figure.dpi':160,'axes.spines.top':False,'axes.spines.right':False})
t=np.linspace(0,10,10001)
fig,axs=plt.subplots(2,2,figsize=(11,8),layout='constrained')
colors=['#2463a5','#d66017']
result={'a_per_m':A_EXP,'weight_per_s':WEIGHT,'scenarios':{}}
for q,color in zip([.02,0],colors):
    label=f'Final distance {q*100:g} cm'
    d=distance(t,q);rate=WEIGHT*np.exp(-A_EXP*d)
    old=100*(.15-d)
    axs[0,0].plot(t,d*100,color=color,label=label)
    axs[0,1].plot(t,rate,color=color,label='New: '+label)
    axs[0,1].plot(t,np.where((t>3)&(t<6),100*(.15-q)/3,0),color=color,ls='--',alpha=.65,label='Old: '+label)
    ax=axs[1,0 if q==.02 else 1]
    ax.plot(t,old,color='#2463a5',ls='--',label=f'Old: total {old[-1]:.3f}')
    ax.plot(t,cumulative(t,q),color='#d66017',label=f'New: total {cumulative(t,q)[-1]:.3f}')
    ax.set_title(label+' — cumulative reward')
    ax.set_ylabel('Undiscounted reward');ax.legend()
    analytic=WEIGHT*integral(q)
    numeric=float(np.trapz(rate,t))
    ts=np.arange(1,501)*.02
    discrete=float(np.sum(WEIGHT*np.exp(-A_EXP*distance(ts,q)))*.02)
    assert abs(analytic-numeric)<1e-6
    result['scenarios'][str(q)]={'old_total':float(old[-1]),'new_integral':analytic,'trapezoid_dt_0_001':numeric,'post_step_sum_dt_0_02':discrete,'log_normalized_by_10':analytic/10}
axs[0,0].set(title='Specified reference trajectories',ylabel='XY goal distance (cm)');axs[0,0].legend()
axs[0,1].set(title='Goal Distance reward rate',ylabel='Reward / s');axs[0,1].legend(fontsize=8)
for ax in axs.flat:
    ax.set_xlabel('Time (s)');ax.set_xlim(0,10);ax.grid(alpha=.2)
fig.suptitle('Goal Distance: weighted rate = 3.7 exp(-20 d), d in meters',fontsize=13)
fig.savefig(OUT/'goal_distance_trajectory_comparison.png');plt.close(fig)
x=np.linspace(0,.15,1501)
fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
axs[0].plot(x*100,WEIGHT*np.exp(-20*x),color=colors[0]);axs[0].set(title='New Goal Distance: instantaneous rate',xlabel='XY goal distance (cm)',ylabel='Reward / s')
def hold(d,r,outer=False):
    inside=8*2**(-(d/r)**2)*(1+np.maximum(1-d/r,0)**2)
    outside=4*np.maximum((.06-d)/(.06-r),0)**2 if outer else np.zeros_like(d)
    return np.where(d<=r,inside,outside)
for r,outer,label,color,style in [(.01,False,'Current: r = 1 cm',colors[0],'--'),(.02,False,'Radius only: r = 2 cm','#777777',':'),(.02,True,'Proposed: r = 2 cm, R = 6 cm',colors[1],'-')]:
    xx=np.linspace(0,.08,1601)
    axs[1].plot(xx*100,hold(xx,r,outer),color=color,ls=style,label=label)
axs[1].set(title='Goal Hold: valid target, zero speed',xlabel='XY goal distance (cm)',ylabel='Reward / s',xlim=(0,8));axs[1].legend(fontsize=8)
for ax in axs:ax.grid(alpha=.2)
fig.savefig(OUT/'distance_and_hold_curves.png');plt.close(fig)
assert abs(WEIGHT*integral(.02)-13)/13 < .01
assert WEIGHT*integral(0)>15
assert np.isclose(hold(np.array([.02]),.02,True)[0],4)
assert hold(np.array([.06]),.02,True)[0]==0
(OUT/'calibration.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
