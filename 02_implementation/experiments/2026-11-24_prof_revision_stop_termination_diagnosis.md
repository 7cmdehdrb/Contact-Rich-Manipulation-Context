# Prof Revision 두 체크포인트의 정지·속도 종료 가설 검증

2026-11-24. 사용자 관찰인 “목표까지 밀지만 정지하지 못하고, 역방향 비용을 피하려 팔 속도 종료를 유발한다”를 로그와 실제 정책 재생으로 검증했다. 환경·보상·종료·PPO 소스와 원본 학습 로그는 수정하지 않았다.

## 결론

**목표 근처에서 정지·유지하는 대신 싼 속도 종료로 미래 손실을 끊는 보상 구조와 행동 패턴은 강하게 지지된다. 다만 “목표 반경 밖으로 크게 넘긴 뒤 역방향 비용을 받고 종료”가 일반적인 사건 순서라는 설명은 지지되지 않는다.** 목표 중심 평면을 조금 지나는 것과 성공 반경3cm 밖으로 이탈하는 것은 다르다. 정상 재생에서는 목표 진입 후 반경 밖 이탈이 없었다. 종료 전 역방향 비용을 이미 받는 경우와 종료와 같은 step에 받는 경우도 구분했다.

일회성 Arm Joint Velocity Termination 비용은 **0**이다. `arm_joint_velocity` 보상은 매 step의 `−0.03 × min(관절 속도 제곱 합,100) × 0.02` 연속 비용이다. 1rad/s 초과 종료 자체에 −3을 지급하지 않는다. 보상 목록의 −3인 `shelf_failure`와 Action Limit 비용은 별개다. 이 환경은 Single Contact v1의 추가 팔 종료 비용을 사용하지 않는다.

## 실행 범위와 정의

- 입력: `logs/TEMP/2026-11-24`의 v0 `model_6100.pt`, Reach5cm `model_7950.pt`. 체크포인트 SHA256은 각 metadata에 보관했다.
- 정상 재생: 각 체크포인트64환경 × seed42·43 × 환경별 처음3episode = 각384회. 길이가 짧은 환경이 표본을 독점하지 않도록 환경별 quota를 적용했다.
- 비교 재생: 같은 seed와64환경에서 팔 속도 종료 threshold만1→무한대로 변경, 환경별 첫1episode = 각128회. 다른 보상·종료·관측 noise·물리·정책은 유지했다.
- `play.py`와 동일한 config/checkpoint 호환 처리, CurriculumOnPolicyRunner, RSL wrapper, 결정론적 inference mean을 사용했다. GUI·영상 export 없이 headless로 계측했다. 학습 로그는 탐색 action을 포함하므로 정상 play의 성공 반경 진입률과 동일한 분포로 취급하지 않는다.
- physics dt0.01s, policy dt0.02s, timeout10s, 성공 반경3cm다. 성공은 timeout에서만 판정되며 보상 항에 별도 성공 bonus·목표 정지 유지 보상이 없다.
- 원래 RewardManager.compute를 한 번 호출한 직후, 자동 reset **이전**의 항별 실제 기여·총합·현재 추적 가시 OBB 중심·목표·속도·action·종료 flag를 저장했다. 매 step 항별 합과 반환 총보상의 일치를 검사했다.
- 목표 중심 통과: episode 초기 타겟→목표 방향에 수직인 목표 평면을 통과한 경우다. 2D 목표 거리/성공 반경 이탈과 별도로 센다. episode1·2는 첫 기록된 물리 step의 타겟 위치를 방향 기준으로 삼았다.

## 학습 로그

체크포인트 iteration을 포함해 직전100개 기록의 산술평균이다. 로그의 사건 비율은 logger 집계값 평균이며, 원시 episode 수를 합산한 비율로 제시하지 않는다. `Episode_Reward/*`는 RewardManager가 **최대 episode 길이10초로 나눈 값**이므로 아래 표에서는10을 곱해 episode 보상 규모로 복원했다. 실제 약1.3초를 곱하지 않는다.

| 항목 | v0 /6100 | Reach5cm /7950 |
| --- | ---: | ---: |
| 팔 속도 종료 로그 평균(%) | 99.86639 | 99.76468 |
| 평균 episode 길이(s) | 1.29620 | 1.30817 |
| 최종 목표 거리(cm) | 2.20206 | 2.05167 |
| 최소 목표 거리(cm) | 2.04425 | 1.87068 |
| Sweep 진행 보상 | 6.78994 | 7.01047 |
| 역방향 비용 | -0.03389 | -0.03810 |
| 팔 속도 연속 비용 | -0.05556 | -0.05872 |
| 손 속도 연속 비용 | -0.38552 | -0.38682 |
| 손 Action Limit 비용 | -0.37325 | -0.37072 |
| 성공 로그 평균(%) | 0.00000 | 0.00000 |

종료 비율은 약1000iteration부터 이미99.7% 수준이었다. 마지막에 새로 나타난 큰 overshoot 현상으로만 해석할 수 없다. 전체 추세와 원시 scalar는 산출물에 보관했다.

## 정상 정책 재생

| 항목 | v0 | Reach5cm |
| --- | ---: | ---: |
| 평가 episode 수 | 384 | 384 |
| 팔 속도 종료 | 383/384 (99.74%) | 381/384 (99.22%) |
| 목표3cm 진입 | 330/384 (85.94%) | 347/384 (90.36%) |
| 진입 후3cm 밖 이탈 | 0/330 (0.00%) | 0/347 (0.00%) |
| 목표 중심 평면 통과 | 205/384 (53.39%) | 226/384 (58.85%) |
| 평균 길이(s) | 1.34479 | 1.34031 |
| 평균 최종 거리(m) | 0.01668 | 0.01573 |
| Sweep 진행 보상 | 7.87781 | 8.13899 |
| 역방향 누적 비용 | -0.04016 | -0.05502 |
| 팔 속도 누적 비용 | -0.05766 | -0.06064 |
| 종료 step 팔 속도 비용 | -0.00183 | -0.00167 |
| 목표 최소 거리 이후 역방향 비용 | -0.03795 | -0.05344 |
| 목표 평면 통과 후 종료 이전 역방향 비용 | 84/384 (21.88%) | 108/384 (28.12%) |
| 성공 | 0/384 (0.00%) | 0/384 (0.00%) |

여기서 “종료 이전 역방향 비용”은 목표 평면 통과 이후 **마지막 종료 step을 제외한** 역방향 비용 합이−0.001 미만인 경우다. 약0.05mm 이상의 누적 거리 증가를 뜻한다. 마지막 step의 비용과 종료가 동시에 발생했다면 이미 비용을 받고 다음 행동으로 종료했다는 증거로 세지 않았다.

- v0: 목표 진입 후 속도 종료 표본329회에서 진입→종료 평균0.126s, 최소 거리→종료 평균0.020s. 종료 step의 Arm action 변화 L2 평균1.515, 그 전 episode 내 변화 L2 중앙값의 표본평균0.504. 이는 말기 동작 변화와 일치하지만 의도나 원인을 단독으로 확정하는 지표는 아니다.
- Reach5cm: 목표 진입 후 속도 종료 표본347회에서 진입→종료 평균0.121s, 최소 거리→종료 평균0.021s. 종료 step의 Arm action 변화 L2 평균1.153, 그 전 episode 내 변화 L2 중앙값의 표본평균0.510. 이는 말기 동작 변화와 일치하지만 의도나 원인을 단독으로 확정하는 지표는 아니다.

역방향 비용은 목표 거리 증가1mm당−0.02다. 종료 step의 연속 팔 속도 비용은 위 표처럼 약−0.002이므로, 그 step의 작은 추가 비용으로 이후 비용이 차단되는 구조다. episode 전체 팔 속도 비용과 “종료 자체의 일회 비용”을 혼동하지 않았다.

## 속도 종료를 해제한 진단용 재생

동일 초기 장면/초기 관측을 확인했지만 자동 reset의 난수 소비와 접촉 물리 때문에 정상 재생과 비교 재생의 모든 prefix가 동일하지는 않았다. 따라서 서로 다른 두 궤적의 끝을 억지로 연결해 인과 효과로 제시하지 않았다. 각 **비교 재생 궤적 자체에서 처음 실제 팔 속도1rad/s를 초과한 step**을 가상 절단점으로 삼았다. 원래 종료했다면 그 뒤 보상은0이며, 같은 정책을 계속 실행한 실제 suffix의 항별 보상을 계산했다.

이 비교는 현재 정책을 계속 실행하는 것과 해당 시점에 episode를 끝내는 것의 손익이다. 적절히 제동한 다른 정책과의 비교나 재학습 ablation이 아니다.

| 속도 최초 초과 이후 항목 | v0 | Reach5cm |
| --- | ---: | ---: |
| 유효 최초 초과 표본 수 | 127 | 126 |
| 계속 실행 시 손실인 표본 | 124/127 | 124/126 |
| discount 적용 후 손실인 표본 | 123/127 | 120/126 |
| 추가 총보상 | -4.91961 | -21.76594 |
| 추가 보상 γ=0.98 할인값 | -2.84099 | -3.39365 |
| 추가 역방향 비용 | -1.14111 | -1.48480 |
| 추가 팔 속도 비용 | -0.10415 | -0.50214 |
| 추가 선반 실패 비용 | -2.57480 | -2.16667 |
| 추가 선반 충돌 비용 | -0.43880 | -0.77295 |
| 추가 손 속도 비용 | -0.22215 | -0.69070 |
| 추가 팔 Action Limit 비용 | -0.27370 | -6.21474 |
| 추가 손 Action Limit 비용 | -0.36483 | -7.24397 |

각128회 중 팔 속도 최초 초과 전에 다른 실패로 끝난 v0 1회·Reach5cm 2회는 절단점 손익에서 제외했다. 정상/비교 궤적의 prefix 일치 기준(중심 오차1mm 미만·action 최대차0.01 미만)을 충족한 표본은 각각2/127·2/126뿐이다. 그래서 서로 다른 rollout 간 차이는 인과 추정량으로 사용하지 않았다.

Reach5cm의 비할인 총손실 평균은 장시간 계속되는 일부 궤적의 큰 Action Limit 비용에 영향을 받는다. 종료 이후의 상태는 원래 정책의 학습 분포 밖으로 진행할 수 있으므로 이를 그대로 “예상했던 미래 손실”로 해석하지 않는다. 총손실 중앙값과 짧은 구간을 별도로 확인했다.

| 강건성 확인 | v0 | Reach5cm |
| --- | ---: | ---: |
| 추가 총보상 중앙값 | -4.25510 | -5.38584 |
| 추가 할인 보상 중앙값 | -3.08306 | -3.16604 |
| 처음0.2초(10step) 추가 보상 평균 | -0.85888 | -0.64518 |
| 처음0.2초 추가 보상이 음수인 표본 | 116/127 | 119/126 |

종료를 해제하면 역방향 비용뿐 아니라 이후 선반 실패 등도 추가된다. 따라서 “역방향 비용 회피만이 원인”이라고 좁히면 안 된다. **추가 실패 비용 없이 조기 종료할 수 있고, 정지·유지의 명시적 양의 유인이 약한 조합**이 핵심이다. 이 비교에서 속도 종료를 해제한 설정은 진단용이며 환경 변경안으로 적용하지 않았다.

## 신호와 인과 해석의 한계

Actor는 초기 타겟 OBB snapshot을 현재 EEF 기준으로 변환한 값, 목표 위치, 손끝/관절, tactile·F/T를 본다. 추적 중인 실제 타겟 위치와 물체 속도는 직접 입력되지 않는다. 보상과 성공만 실제 추적 가시 중심을 사용한다. 목표에 가까운 손 위치 신호 자체가 전혀 없다는 뜻은 아니지만, 실제 물체의 현재 위치·속도에 대한 직접 피드백이나 목표 근처 감속·정지 유지 보상은 없다.

관측 제약이 정지 실패의 원인인지는 관측/보상별 ablation 없이 분리할 수 없다. 고정 정책의 손익 실험과 말기 행동은 종료 활용과 일치하며 보상 구조의 유인을 검증하지만, “정책이 의도적으로 역방향 비용을 받은 뒤 종료를 선택하도록 학습됐다”는 학습 인과는 입증하지 않는다. 재학습·보상 수정·장기 성공률 개선 실험은 수행하지 않았다.

## 변경·보존·검증

변경 전에는 두 실행의 학습 로그와 checkpoint만 있었고, 이번 작업으로 `outputs/prof_revision_stop_diagnosis/`에 읽기 전용 진단 실행기·분석기·원시 trace·CSV·그림을 추가했다. 개발 문서에는 이 기록만 추가했다. 활성 패키지의 디렉토리·함수·수치·등록·PPO는 변경하지 않았다. 비교 실행의 팔 종료 threshold override는 해당 프로세스의 manager 설정에만 적용했다. `logs/rsl_rl`과 원본 TEMP 로그를 정리하거나 이동하지 않았다.

- 학습 시 저장된 env.yaml과 live config를 재귀 대조: 공통 차이는 환경 수2048→64와 결과 저장 경로다. Reach5cm는 학습 PC의 robot USD 절대경로가 현재 PC의 같은 패키지 상대 asset으로 바뀌었다. 로컬 자산 SHA256을 저장했으며 원격 원본 자산의 byte 동일성은 독립 검증하지 않았다.
- 매 step 보상 합 일치, 저장 trace 유한성, 환경별 episode quota 완료를 검사했다. checkpoint는 실행 전후 SHA256 일치를 확인했다.
- 진단 Python 파일 전체 py_compile 통과. 새 Markdown2개 math 검사 통과, 문서 링크 검사2개 파일의 internal1/external11개 오류0, workspace·문서 저장소 git diff --check 통과. 그림2개를 렌더링 후 눈으로 확인했다.
- 초기 실행기의 RSL deprecated 설정 변환 누락과 inference tensor의 수동 reset 범위 오류를 수정했다. 한 차례 비교 재생의 native segmentation fault가 있었으며 해당 미완료 결과는 통계에 포함하지 않고 재실행했다. 최종 완료 결과만 분석했다. native crash 원인은 검증하지 않았다.
- 최초 v0 seed42 정상192회는 완료되어 보존하고 재시작 시 재사용했다. 진단 watchdog은 모델 초기화 이후 중단하도록 바꿨다. 이후 최종 정상·비교 데이터는 각각 환경별 quota를 충족했다.
- 두 시뮬레이터 프로세스는 독립적이다. 일부 실행 시간이 겹쳤으므로 wall-clock 성능이나 collection benchmark로 사용하지 않는다.
- 미검증: GUI 영상의 사용자 시점 재확인, 다른 checkpoint·다른 seed 모집단, 학습 정책의 동기/인과, 수정 보상의 재학습 효과, native crash 원인.

## 산출물과 재현

- [원시 결과·실행기](../../../../outputs/prof_revision_stop_diagnosis/)
- [학습 scalar 요약](../../../../outputs/prof_revision_stop_diagnosis/training_summary.json) · [학습 추세](../../../../outputs/prof_revision_stop_diagnosis/training_dynamics.png)
- [전체 재생 요약](../../../../outputs/prof_revision_stop_diagnosis/play_summary.json) · [대표 종료 timeline](../../../../outputs/prof_revision_stop_diagnosis/terminal_timelines.png)
- [v0 episode](../../../../outputs/prof_revision_stop_diagnosis/prof_v0/episodes.csv) · [v0 절단점 손익](../../../../outputs/prof_revision_stop_diagnosis/prof_v0/virtual_cutoff.csv)
- [Reach5cm episode](../../../../outputs/prof_revision_stop_diagnosis/reach5cm_v0/episodes.csv) · [Reach5cm 절단점 손익](../../../../outputs/prof_revision_stop_diagnosis/reach5cm_v0/virtual_cutoff.csv)
- [설정·체크포인트 대조](../../../../outputs/prof_revision_stop_diagnosis/audit.json) · [소스·실행기 해시](../../../../outputs/prof_revision_stop_diagnosis/source_hashes.json)

Workspace 루트에서 기존 Isaac Lab 환경의 Python으로 실행한다. `--resume`는 이 진단 디렉토리에 완료된 trace가 있으면 재사용하므로 완전 재실행은 새 output 디렉토리를 지정한다.

```bash
python outputs/prof_revision_stop_diagnosis/probe.py \
  --task Inspire-Sweep-Prof-Revision-v0 \
  --checkpoint logs/TEMP/2026-11-24/inspire_sweep_prof_revision_v0/2026-11-24_00-27-46/model_6100.pt \
  --output outputs/prof_revision_stop_diagnosis/prof_v0 --headless
python outputs/prof_revision_stop_diagnosis/probe.py \
  --task Inspire-Sweep-Prof-Revision-Reach5cm-v0 \
  --checkpoint logs/TEMP/2026-11-24/inspire_sweep_prof_revision_reach5cm_v0/2026-11-24_01-06-28/model_7950.pt \
  --output outputs/prof_revision_stop_diagnosis/reach5cm_v0 --headless
python outputs/prof_revision_stop_diagnosis/read_training.py
python outputs/prof_revision_stop_diagnosis/analyze.py
python outputs/prof_revision_stop_diagnosis/figures.py
python outputs/prof_revision_stop_diagnosis/audit.py
```

기준 workspace commit: `19cac187345419cc08be097d7148052ddf3e383b`, 문서 저장소 기준 commit: `33858ea1086f22f1154eb799d934475af5de589f`. 시작 시 사용자 변경인 `docs/SSH.md` 및 서브모듈 현재 커밋을 보존했다. 활성 패키지의 tracked diff는 없다.
