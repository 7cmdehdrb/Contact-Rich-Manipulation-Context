# Wrench Refactor: 정책 입력 Action Rate의 네 파생 환경

2026-11-06. [최종 환경 계약](../environments/WRENCH_REFACTOR_POLICY_RATE_ENVIRONMENTS.md).

## 요청과 작업 기준

사용자는 기존 v0/v1/v2/v3를 각각 상속한 v0_1/v1_1/v2_1/v3_1을 만들고, 앞서 비교한 raw 정책 출력 변화 비용을 실제 Action Rate 보상으로 사용하도록 요청했다. max 제한 제거를 허용했다. 대화의 활성 대상인 Wrench-Refactor 계열로 해석하여 작업 시작 시 명시했다.

workspace 기준commit은 `89833ab4b5017ae91ba140d06d8add9393907dad`이며, 작업트리에는 기존 사용자 변경과 앞선 v3-Test 계측/paired-play 변경이 누적되어 있었다. 기존 수정·독립 문서 저장소 commit·학습 로그는 보존한다. 새 commit을 만들지 않는다.

## 변경과 영향

- 같은 기존 파일에 네 EnvCfg·네 PPO·네 Gym 등록을 추가했다. 각 EnvCfg/PPO는 대응하는 원본 버전을 직접 상속한다.
- `mdp/reward_functions/wrench_refactor.py`에 stateless `policy_action_rate_penalty`를 추가했다. 각 자식의 post_init에서 기존 term의 func만 이 함수로 교체했다.
- 기존 정규화 OSC 출력토크 변화 → raw 정책 Arm6D action 변화. Arm계수0.03·Hand계수0.03·Hand clamp0–1·term weight−1은 보존하며 Arm합산cap100만 제거했다. 입력 action 자체는 clamp하지 않는다.
- 부모의 `RefactorActionRatePenalty`와 v3-Test 비교 출력은 보존했다. 다른 모든 reward·term 순서·params·종료·커리큘럼·Scene·Command·reset·관측·제어·runtime은 부모를 유지했다. PPO 차이는 각자 experiment_name뿐이다.
- 목표는 부모의 양쪽 방향이며 Arm 속도 종료3rad/s도 유지한다. v3-Test에서의 임시왼쪽전용/종료해제/print를 새 학습 환경에 복사하지 않았다.

## 전체 대조와 검증

기존 `_wrench_refactor_probe.py`를 확장하여 실제 config 전체 to_dict를 부모/자식별로 비교한다. 새 환경에서 기대하는 유일한 값 차이는 robot_action_rate_penalty.func이며, PPO는 experiment_name뿐이다. 모든 직접부모 클래스도 검사하고 자식 구성 후 부모 snapshot 불변을 확인한다.

CPU 새 검사는 unbounded raw action 변화·위치/회전 동일계수·Hand clamp·일부env 이전action 변경·reset시 이전action0·입력 텐서 무변경을 확인한다. CPU 회귀60개 통과(5.60초).

첫 GPU probe는 config.to_dict가 func를 문자열로 직렬화하는데 callable 객체로 기대값을 만든 검증 코드 오류로 `Unexpected v5 environment delta`에서 중단했다. 실제 func identity는 별도 검사하고 전체dict의 func는 동일 직렬화 형식으로 비교하도록 검증을 수정했다. 환경 코드의 동작 오류로 해석하지 않는다.

GPU 각 환경2개씩의 실행 명령은 다음 패턴이다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/tests/_wrench_refactor_probe.py --task Inspire-Wrench-Refactor-v0_1 --num_envs 2 --headless --device cuda:0 --output outputs/wrench_refactor_policy_rate/v0_1
```

v1_1/v2_1/v3_1도 task와output의버전을 바꿔 순서대로 실행한다. 실제 Gym 생성·관측74/74/64/64·17물체·오른손/EEF·control축·물성·부분reset·iteration0/9999/10000/13000/16000/19000/22000/25000에서각36step rollout을 검사한다. 새 환경에서는 ±0.25 Arm action을 번갈아 입력하고 매step 실제 RewardManager에 기록된 term 비용이 새 함수값×weight−1과 같은지 미종료env에서 대조한다. 속도 종료 term 활성과 새 reward callable identity도 검사한다.

산출물은 `outputs/wrench_refactor_policy_rate/v0_1`부터`v3_1`까지, 실행로그는 `/tmp/wrench_refactor_policy_rate_v0_1.log`부터`v3_1.log`까지다. 학습·대규모rollout·후보로재학습한정책성능은 이번 검증 범위가 아니다.

## 최종 결과

네 환경 모두GPU probe가exit0으로완료됐고각probe_2.json의policy_action_rate=True, left_only=False, 부분reset/고정물성/유한rollout=True를확인했다. v0_1/v1_1/v2_1은root OSC, v3_1은EEF OSC로부모계약을유지했다. 실제RewardManager term값과새함수계산의일치검사를통과했다. 전체설정·직접상속·PPO비교도네실행모두통과했다. 통합산출물은 `outputs/wrench_refactor_policy_rate/summary.json`이다.

변경문서5개math검사통과. 링크272개검사에서기존README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락링크1개가검출됐으며신규링크는정상이다. 기존누락문서는요청범위밖으로보존했다. 패키지코드와문서저장소diff whitespace검사통과. 학습은실행하지않았으며정책성능및장기학습안정성은미검증이다.
