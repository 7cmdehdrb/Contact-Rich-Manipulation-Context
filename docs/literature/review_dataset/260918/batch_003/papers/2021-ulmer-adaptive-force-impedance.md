# Learning Robotic Manipulation Skills Using an Adaptive Force-Impedance Action Space

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B081`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Maximilian Ulmer; Elie Aljalbout; Sascha Schwarz; Sami Haddadin
- Year: 2021
- Venue: arXiv preprint
- DOI / arXiv: Not stated / 2110.09904v2
- PDF version: arXiv v2 (2110.09904v2, 20 Oct 2021)
- Page count: 8
- SHA-256: `0df3961d91d9065f9c5bef03fda4f22be180e5a84cdd5060014bbd775e5718fc`
- PDF filename: Ulmer 등 - 2021 - Learning Robotic Manipulation Skills Using an Adaptive Force-Impedance Action Space.pdf
- 확인 범위: 전체 arXiv PDF pp.1-8; AFORCE equations, real/sim observations, controller frequencies, comparisons, limitations/future work 확인

## 2. Relevance to This Review

`Relevant`

tactile은 쓰지 않지만 estimated external wrench를 high-rate adaptive force/impedance controller와 저주파 policy observation으로 분리해 사용하는 contact-rich manipulation 연구다. Wrench가 contact locality 대신 force regulation·stability·safety를 담당하는 실제 구조와 그 한계를 분석하는 데 직접 관련된다.

## 3. Task

real robot에서 wiping하고, simulation에서 Door, Lift, Wipe를 학습한다. contact-rich surface interaction에서는 목표 wrench를 유지하면서 motion tracking, stability, energy efficiency를 동시에 최적화한다.

## 4. Method

### 4.1. Overall Pipeline

20 Hz high-level policy/expert가 observation에서 desired pose와 필요 시 desired wrench를 출력 → AFORCE가 robot pose/velocity와 estimated external wrench를 500 Hz-1 kHz로 측정 → feedforward wrench와 stiffness를 error에 따라 적응 → task-space input wrench → Jacobian transpose joint torque. [Secs. IV-B, V, PDF pp.3-6]

### 4.2. Observation

real wipe high-level observation은 current EEF pose, recent external wrench measurements, visually detected wipe-spot centroid이다. 1 kHz low-level measurement는 joints, EEF pose/velocity, estimated external wrench이다. simulation SAC의 task별 exact observation vector는 원문에서 확인되지 않는다. [Sec. V-A, PDF p.5]

### 4.3. Action

AFORCE high-level action은 desired Cartesian pose x_d이며 force task에서는 desired wrench F_d도 포함한다. controller가 stiffness K와 feedforward wrench를 내부 적응한다. [Secs. III-IV, PDF pp.2-4]

### 4.4. Controller

Cartesian adaptive force-impedance controller. K와 F_ff를 tracking error에 따라 연속 적응하고 task-space wrench를 Jacobian transpose로 joint torque로 변환한다. real controller는 1 kHz, simulation low-level은 500 Hz이다. [Eqs. (5)-(8); Sec. V, PDF pp.4-6]

### 4.5. Learning / Optimization Method

simulation high-level policy는 Soft Actor-Critic이며 actor/critic은 1024-unit 2-layer networks이다. real wiping demonstration은 learned RL이 아니라 expert high-level plan으로 controller/action-space 효능을 검증한다. [Sec. V-A-B, PDF p.5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미명시 | simulation RL의 object pose observation vector 미명시; real은 target wipe-spot centroid만 vision으로 제공 | 미명시 | goal centroid를 current object pose로 기록하지 않는다. [Sec. V-A-B, PDF p.5] |
| Orientation | 미명시 | task object orientation observation 미명시 | 미명시 | Door initialization orientation은 simulator가 randomize한다. [Sec. V-B, PDF p.5] |
| Shape / Geometry | 미명시 | CAD/shape actor input 여부 미명시 | 미명시 | task environments are fixed benchmarks. [Sec. V-B, PDF p.5] |
| Physical Parameters | 미제공 | 환경 stiffness/friction parameter input 없음 | No | controller parameters α,β,γ,μ는 manual tuning한다. [Secs. IV-B and VI, PDF pp.4,6] |

## 6. Missing Object Information and Compensation

Environment physical interaction parameters 미제공
→ real-time pose error + estimated external wrench
→ stiffness와 feedforward wrench를 online adaptation하여 contact stability와 motion error를 조절한다. [Sec. IV-B, PDF p.4]

Contact locality/configuration 미제공
→ net external wrench history와 known task plan/goal centroid
→ force magnitude regulation과 overload penalty는 가능하지만 contact point/patch를 복원하지 않는다. 논문은 locality 추정을 목표로 하지 않는다. [Sec. V, PDF pp.5-6]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [전체 PDF pp.1-8]

### 7.2. Preprocessing

사용하지 않음. [전체 PDF pp.1-8]

### 7.3. Policy Representation

사용하지 않음. [전체 PDF pp.1-8]

### 7.4. Retained Information

사용하지 않음. [전체 PDF pp.1-8]

### 7.5. Removed / Unavailable Information

사용하지 않음. [전체 PDF pp.1-8]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

estimated external wrench. 물리 wrist F/T인지 joint torque estimation인지 원문에서 확인되지 않으므로 wrist F/T로 동일시하지 않는다. simulation에서는 simulator contact wrench이다. [Sec. V-A, PDF p.5]

### 8.2. Representation

recent external wrench measurements at 20 Hz for high-level observation; instantaneous estimated wrench at 1 kHz for low-level real control. 원하는 Cartesian wrench F_d와 adaptive F_ff도 controller 내부에 존재한다. [Sec. V-A; Eq. (5), PDF pp.4-5]

### 8.3. Role

desired contact force regulation, tracking-error compensation, stiffness adaptation, contact stability, energy reduction, excessive-force reward penalty/safety evaluation. [Secs. IV-B and V, PDF pp.4-6]

### 8.4. Required Assumptions

robot dynamics/Jacobian과 EEF pose/velocity가 알려지고, estimated external wrench가 controller bandwidth에서 interaction load를 반영하며, task에서 desired force direction/profile이 정의되어야 한다. [Secs. III and IV-B, PDF pp.2-4]

### 8.5. Reported Limitation / Ambiguity

contact location/patch 또는 multi-contact 분해는 제공하지 않고 원문도 이를 직접 논의하지 않는다. reactive adaptation이며 agent가 미리 개입할 수 없고 adaptation parameters는 수동 tuning한다. [Sec. VI, PDF p.6]

## 9. Other Observations

- Proprioception: joint position/velocity, EEF pose/velocity, pose tracking error.
- Vision: real wipe-spot centroid detection에만 사용한다. 저자는 vision-based RL experiment를 future work로 남긴다.
- History: high-level은 recent wrench measurements를 사용한다.
- Previous action: 별도 vector는 명시되지 않는다.
- State estimator: external wrench estimator의 내부 방식은 미명시이다.

## 10. Tactile–Other Modality Relationship

Tactile은 사용하지 않는다. High-level은 task state와 저주파 recent wrench를 보고, low-level AFORCE는 고주파 wrench/proprioception으로 force·impedance를 조절한다. 따라서 wrench는 global interaction load와 regulation에 충분하지만 contact locality/geometry는 복원하지 않는다. fixed/variable impedance 및 force-controller 조합과 비교해 action-space의 효용을 검증한다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not stated | simulation SAC의 exact task observation 미명시 | real expert observation은 EEF pose, recent wrench, visual goal centroid이다. [Sec. V, PDF p.5] |
| Critic | Not stated | SAC critic exact input 미명시 | asymmetric privileged critic을 명시하지 않는다. [Sec. V-B, PDF p.5] |
| Reward | Yes | simulation task completion, marker state, contact force thresholds | simulator가 Door/Lift/Wipe reward와 force penalty를 계산한다. [Sec. V-B, PDF pp.5-6] |
| Termination | Not stated | simulation termination state 미명시 | task evaluation reward와 termination을 혼합하지 않는다. [Sec. V-B, PDF pp.5-6] |
| Curriculum | No | random 5k samples pretraining; task initialization randomization | GT curriculum은 명시하지 않는다. [Sec. V-B, PDF p.5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| AFORCE가 fixed impedance보다 energy-efficient한 real wiping을 한다. | Controlled comparison | AFORCE vs low/mid/high fixed impedance, same force controller | high의 약 절반 energy로 경쟁적인 tracking error; low는 contact 유지 실패. | Sec. V-A; PDF PDF pp.4-5 ; Fig. 2 |
| AFORCE가 manipulation learning을 개선한다. | Controlled comparison | AFORCE vs variable impedance/force action spaces on Door, Lift, Wipe | 모든 task에서 더 빨리 수렴하고 higher maximum reward; variable spaces의 energy/action이 더 큼. | Sec. V-B; PDF PDF pp.5-6 ; Table I ; Fig. 3 |
| force controller만으로 안정적 contact가 보장되지 않는다. | Failure analysis | variable+force and low+force vs AFORCE | 높은 stiffness는 force regulation을 방해하고 low+force는 tool alignment/contact를 잃었다. | Sec. V-B; PDF PDF p.6 ; Fig. 3 |

## 13. Author-stated Limitations

adaptive parameters를 수동 tuning해야 하며 잘못된 값은 learning 성능을 크게 해친다. interaction adaptation은 reactive라 high-level agent가 선제적으로 조절하지 못한다. 모든 action space가 완전히 safe하지 않았고 Wipe의 AFORCE도 12% episodes에서 force penalty가 있었다. [Secs. V-B and VI, PDF p.6]

## 14. Author-stated Future Work

adaptive parameters와 high-level policy를 동시에 학습하고, agent가 adaptation behavior에 개입할 수 있는 방법을 조사한다. vision-based RL 실험도 future work로 남긴다. [Secs. I and VI, PDF pp.2,6]

## 15. Review-relevant Findings

- estimated external wrench의 물리 source는 원문에서 미명시이므로 wrist F/T로 기록할 수 없다.
- high-level은 recent wrench, low-level은 high-rate wrench와 proprioception을 사용한다.
- wrench는 force regulation·stability·safety penalty를 담당하지만 contact locality를 복원하지 않는다.
- simulation SAC reward는 force threshold와 task simulator state를 사용한다.
- action-space comparison과 failure analysis가 force/impedance 역할을 뒷받침한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Sec. V-A, PDF p.5 |
| Object pose | Sec. V-B, PDF p.5; exact vector 미명시 |
| Tactile | 사용하지 않음; 전체 PDF |
| F/T | Sec. V-A and Eq. (5), PDF pp.4-5 |
| Reward | Sec. V-B, PDF pp.5-6 |
| Critic | Sec. V-B, PDF p.5; exact input 미명시 |
| Ablation | Fig. 2, PDF p.4; Fig. 3/Table I, PDF pp.5-6 |
| Limitation | Sec. VI, PDF p.6 |
