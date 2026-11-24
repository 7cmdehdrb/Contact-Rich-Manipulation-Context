# Prof Revision v0_2 구현 기록

2026-11-24. [개발 명세](../../01_plan/environments/2026-11-24_PROF_REVISION_V0_2_SPEC.md) · [실행 계약](../environments/PROF_REVISION_V0.md#prof-revision-v0_2).

## 요청·기준·변경

사용자가 명세 기반 구현을 요청했다. root 기준 `7572d9df73b9bc413c9abe1e1d58def3198add65`, 문서 기준 `3786836b665a226333280944e4275a63c9adf19d`. 사용자 `docs/SSH.md` 변경과 명세 작성 변경을 보존했다. 기존 학습 로그를 수정하지 않았다.

v0 직접 상속 EnvCfg·RewardsCfg·PPOCfg 및 Gym 등록을 추가했다. 기존 역할별 파일에 추가했고 runtime·부모 함수는 수정하지 않았다. 신규 margin 함수는 상태/cache 없이 실제 팔6관절 절대 속도의 최댓값을 읽어 정규화 제곱을 반환한다. 파라미터 유한성·범위를 검사하며 자식 EnvCfg는 margin limit과 종료 threshold 일치를 검사한다.

| 항목 | 변경 전 v0 → v0_2 |
| --- | --- |
| Sweep | ContactSideSweepProgress/1.5·0.7 → 순수 sweep_progress/면 계수1, weight100 유지 |
| Margin | 없음 → clamp((max(abs(팔속도))−0.8)/0.2,0,1)의 제곱, weight−3 |
| Joint 사건 | 없음 → 기존 arm_joint_failure, 일회−3 |
| 보상 수 | 16 → 18, 기존15개 보존·신규2개 뒤에 추가 |
| Formation | 부모 거리 합·weight0.245, 각도 식 없음 |
| 나머지 구성 | 관측·Scene·reset·Command·Action·Termination·빈 Curriculum·runtime 및 PPO 수치 보존 |
| 등록·로그 | 새 task/자식 Cfg, 로그 inspire_sweep_prof_revision_v0_2 |

면 동등성은 목표 방향 힘 정렬 삭제를 의미하지 않는다. 기존 속도 L2 비용도 유지한다. 종료 threshold는 >1.0이고, 새 두 항의 종료 step 기여는 −3.06이다. 속도 margin은 dt 비례, 사건 비용은 dt 무관이다.

## 검증

산출물은 workspace `outputs/prof_revision_v0_2_validation/`에 보관한다. `before.json`은 변경 전 Python SHA256, `audit.json`은 기존 정의/등록 보존 대조다.

CPU 검사:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py
```

61개 통과(3.82초), 기존 ONNX deprecation warning1건. 속도 ±0.8/±1.0 근처, 단조·포화·다중 관절 max·손 제외·시간 적분·잘못된 params·면 정보 없이 동일 Sweep을 검사했다. 기존 테스트의 종료 >경계 및 사건 dt 독립성도 통과했다.

정적 대조에서 생산 코드 기존 정의14개와 기존 등록 호출 모두 AST 동일, 그 밖의 Python 파일 SHA256 보존을 확인했다. 변경 Python은 생산5개·검증script1개·기존test1개로7개다.

첫 GPU 시도는 실제 생성 전에 검증script에서 to_dict가 callable을 문자열로 바꾸는 점 때문에 identity 비교에 실패했다. 실제 cfg callable을 비교하도록 검사만 수정했다. 초기 로그를 `smoke_initial_config_check.log`로 보존했다. Sim 종료 처리로 shell exit0이 나올 수 있어 결과 JSON과 통과 marker를 완료 증거로 사용한다.

실제 GPU·PPO·문서 검사 결과는 아래 후속 기록에 남긴다.

## 해석과 미검증 범위

종료율·성공률·정밀 정지·무동작 개선은 장기 학습/평가가 필요하다. 기존 v0 checkpoint의 고정 정책은 보상 연결과 자연 종료만 검사하며 v0_2 학습 성능을 입증하지 않는다. 2048환경 성능·장기 학습·Play 영상 비교는 수행하지 않았다. 명세의 장기 비교 항목은 후속 연구 평가 기준이다.

## 후속 실행 결과

실제 RTX3090·4환경·seed42 검증 명령:

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_prof_revision.py --task Inspire-Sweep-Prof-Revision-v0_2 --num-envs 4 --checkpoint logs/TEMP/2026-11-24/inspire_sweep_prof_revision_v0/2026-11-24_00-27-46/model_6100.pt --output outputs/prof_revision_v0_2_validation/smoke.json --headless
```

성공 marker와 smoke.json을 확인했다. 전체 EnvCfg는 Sweep 교체·새2항 외 부모와 동일하고 PPO는 실험명만 다르다. Reach5cm의 기존 차이도 보존한다. 보상18개, 부모 Formation 식/weight, 실제 margin rate·순수 진행 기여·reward 총합을 확인했다. 12개 zero-action step의 유한 관측과108/176D, 부분 reset·자동 timeout·고정 OBB/추적 OBB·JIT export가 통과했다. 고정 v0 정책으로 자연 팔 속도 종료4건을 관측했고, reset 전 종료 flag가 실제 최대 절대 속도 >1과 일치했다. 모든 step에서 사건−3/0·margin 수식·보상 합을 검사했으며 종료4건에서 새 두 항 합−3.06이 일치했다. 이 과정은 v0_2 학습 완료 정책 평가가 아니다.

짧은 PPO 명령:

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_2 --num_envs 16 --max_iterations 1 --resilient-attempt-dir outputs/prof_revision_v0_2_validation/ppo_smoke --resilient-target-iterations 1 --logger tensorboard --headless
```

16환경×36step=576transition, PPO1회 업데이트 완료. collection4.849초·learning0.565초, value loss3.4310·surrogate−0.0406·entropy17.0132. `ppo_smoke/model_0.pt`의 모델/optimizer 포함132개 Tensor 유한, optimizer step32, TensorBoard77개 scalar tag 모두 유한을 확인했다(`ppo_check.json`). 기존 `logs/rsl_rl` 경로를 사용하지 않았다. 소수 환경 단발 실행이므로2048환경 성능이나 장기 수렴을 입증하지 않는다.

문서 검증: 구현 관련5개 Markdown math 통과, 상대 링크 internal400/external1 오류0. README 신규 두 링크 파일·anchor를 별도로 확인했다. 두 저장소 `git diff --check` 통과. 브라우저 렌더링은 수행하지 않았다.

최종 대조: 생산 코드 기존14개 정의/기존 등록 보존과 부모 전체 설정 대조를 함께 통과했다. 요청한 두 기능은 Sweep 면 선호 삭제와 속도 위험/종료 비용이며, Formation·관측·종료·물리·제어·PPO 수치에 추가 변화가 없다. 장기 성능 비교는 후속 실험 범위다.
