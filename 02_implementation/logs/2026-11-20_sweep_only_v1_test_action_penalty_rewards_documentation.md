# Sweep Only v1 Test ActionPenalty 보상 상세 문서 작성

## 요청과 기준

사용자는 로그 이름 `inspire_sweep_only_v1_test_action_penalty`에 해당하는 환경의 보상·페널티를 상세히 정리한 문서 하나를 요청했다. 모든 보상식을 step t에 받는 값으로 구성하고, 식에서 시간 간격을 의도적으로 제외하도록 명시했다.

작업 기준 workspace HEAD는 `dd68f9d3e79ee447dcbdab2183a2b32f6ff7fb46`, 문서 submodule HEAD는 `5074b42a1db5861a4f76d8ebeced425d242e9800`이다. 시작 시 workspace에는 문서 submodule 참조 차이만 표시됐고 문서 저장소 내부와 환경 소스에는 미커밋 변경이 없었다. 현재 commit·submodule 참조를 보존하고 문서만 추가·연결했다.

## 변경 전후와 의도

| 대상 | 변경 전 | 변경 후 |
| --- | --- | --- |
| 보상 상세 문서 | 일반 Sweep Only·계열·ActionPenalty 설명에 정보가 분산됨 | [v1-Test-ActionPenalty 보상 문서](../environments/SWEEP_ONLY_V1_TEST_ACTION_PENALTY_REWARDS.md) 하나에서 15개 term·총 보상식·5개 커리큘럼을 설명 |
| 계열 안내 | 신규 상세 문서 링크 없음 | ActionPenalty 절에 한 문단으로 연결 |
| 환경·학습 코드 | 현재 실행 설정 | 변경 없음 |

요청 대상은 `Inspire-Sweep-Only-v1-Test-ActionPenalty`이며 `SweepOnlyV1TestActionPenaltyEnvCfg`가 `SweepOnlyV1TestEnvCfg`를 직접 상속한다. 일반 물체 옆 IK의 `v1-ActionPenalty`, 계수를 강화한 `v1_2-Test`, Deadzone 0°의 `v2-Test`와 구분했다. 보상·페널티 자체의 변경 요청은 아니므로 함수·weight·params·일정·종료·등록·PPO·관측·Action을 수정하지 않았다.

## 최종 코드 대조

- Sweep 정방향 50·후퇴 −10, 접촉 카운트 0–20·정규화 count/20, 최근 3구간 중 2구간 접촉과 상판 위 12cm 미만 조건을 확인했다.
- 현재 타겟–손 법선·마찰 합력의 구간 평균과 법선 하중의 합을 구분하고, 방향 계수 분모가 3D 힘 norm임을 기록했다.
- Test Reach는 `InverseDistanceReach`, weight30·near radius0.1·distance scale0.1이다. reset 시 물체 원점 기준 간격과 현재 bounds 중심 기준 근접도의 차이를 명시했다. 최고 접근 기록이나 잔여 budget 차감으로 설명하지 않았다.
- 원본 12D 행동 변화 제곱합과 신규 허용 범위 초과 제곱평균을 구분했다. 팔 6·손 6 행동과 손 물리 12관절 속도 대상의 차이도 기록했다.
- 선반 근접 term의 높이1.06과 접촉·실패 기준1.05, 선반 이동만으로 종료될 때 정액−3이 반드시 발생하지 않는 조건을 확인했다.
- 장애물 접촉·wrench 변화의 초기 weight0과 최종값, 250 iteration 단위 보간을 포함한 5개 일정 전체를 대조했다. `max_positive_fraction=None`이므로 wrench의 양의 보상 budget 제한은 없다고 기록했다.
- 활성 물체의 기울기와 활성 장애물의 3D 이동 비용은 시각 관측 여부와 무관함을 기록했다. 성공·timeout 자체의 bonus가 없고 성공 경계는 엄격한3cm 미만임을 확인했다.
- 시간 간격을 생략한 식이 모든 연속형 term에서 원시 step reward 수치와 같지는 않다는 표기 규칙을 첫 문단에 명시했다. 숫자로 시간 간격을 숨겨 넣지 않았다.

## 검증과 한계

환경을 import하거나 시뮬레이터를 시작하지 않는 일회성 Python AST 검사로 실제 RewardCfg 클래스 정의를 구성용 대역 객체와 함께 평가했다. v1의 두 weight override와 ActionPenalty의 두 term을 적용한 결과 **15개 term의 이름·weight·callable 이름**이 상세 문서 표와 대응했다. 실제 IsaacLab configclass·RewardManager를 생성한 검사는 아니며, 상속·설정의 정적 대조다. Reach 파라미터와 wrench budget 해제도 확인했다.

실제 `scheduled_value` 함수를 AST로 불러 5개 schedule의 모든 knot를 확인했다. 문서의 예시인 iteration2000의 obstacle/wrench weight −0.01/−0.015, iteration2250의 −0.0125/−0.01875와 일치했다. **28개 math block 모두 시간 간격 인자를 포함하지 않는 것**을 검사했다.

최초 보조 검사에서 callable 이름을 literal로 평가하려 한 AST 검사기 오류와 math block 개수를 임의 상수로 가정한 집계 오류가 있었다. 검사 범위를 literal params로 좁히고 실제 block 개수를 사용해 수정했다. 최초 Markdown 검사에서 inline 수식의 간격·집합 escape가 지적돼 단순 표기로 고쳤다. 환경 코드 문제나 계산식 변경은 없었다.

문서 수식·링크·공백 검사는 아래 명령으로 수행했다. 최종 결과는 **Markdown 수식 3파일 통과, 내부 링크17개·외부 workspace 링크27개 오류0, workspace·문서 저장소 모두 `git diff --check` 통과**다. 최종 작업트리 차이는 상세 문서·이 로그의 신규 생성과 계열 안내 링크 추가뿐이다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/environments/SWEEP_ONLY_V1_TEST_ACTION_PENALTY_REWARDS.md \
  02_implementation/environments/SWEEP_ONLY_FAMILY.md \
  02_implementation/logs/2026-11-20_sweep_only_v1_test_action_penalty_rewards_documentation.md

python 00_guidelines/scripts/check_document_links.py --check-external \
  02_implementation/environments/SWEEP_ONLY_V1_TEST_ACTION_PENALTY_REWARDS.md \
  02_implementation/environments/SWEEP_ONLY_FAMILY.md \
  02_implementation/logs/2026-11-20_sweep_only_v1_test_action_penalty_rewards_documentation.md

git diff --check
```

GPU·Isaac Sim·학습·기존 checkpoint 평가는 실행하지 않았다. 코드와 문서의 대조만 수행했으며 장기 학습 성능이나 화면상의 수식 렌더링을 새로 검증한 것은 아니다. `logs/rsl_rl`을 포함한 학습 로그·프로세스·기존 checkpoint는 변경하지 않았다.

## 후속 요청: 현재 Reach와 제안한 선형 Reach 그래프

사용자가 현재 항과 제안 항을 그래프로 비교해 달라고 요청했다. 현재 항은 최대값0.8, 즉 초기 EEF–물체 원점 거리 약36.7cm를 가정한 역거리 곡선으로 고정하고, 제안 항은 가중치0.8·근접 반경10cm·선형 감소 폭35cm·45cm 이후0으로 그렸다. 초기 거리 분포의 실측 결과가 아니며 제안식을 환경에 적용한 작업도 아니다. 보상식의 시간 간격 생략 규칙은 유지했다.

산출물은 [PNG 그래프](../../../../outputs/reaching_reward_comparison/reaching_reward_comparison.png), [SVG 그래프](../../../../outputs/reaching_reward_comparison/reaching_reward_comparison.svg), [계산 데이터](../../../../outputs/reaching_reward_comparison/reaching_reward_comparison.csv), [재생성 스크립트](../../../../outputs/reaching_reward_comparison/plot_reaching_rewards.py)다. 변경 전에는 비교 그래프가 없었고, 변경 후 출력 디렉터리에만 이 산출물이 추가됐다. 기존 상세 문서의 현재 보상식과 환경 소스·등록·학습 설정에는 변경이 없다.

CPU Matplotlib으로 0–60cm를0.05cm 간격으로 계산하고, 35cm의 교점·제안 보상0–0.8 범위·45cm 이후0을 assertion으로 확인했다. 생성된 PNG를 열어 한글·축·범례·주석과 곡선을 육안 확인했다. 실행 명령은 workspace 루트에서 다음과 같다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python outputs/reaching_reward_comparison/plot_reaching_rewards.py
```

후속 기록의 Markdown 수식 검사1파일, 내부 링크1개·외부 산출물 링크4개 오류0, 두 저장소의 공백 검사를 통과했다. GPU·Isaac Sim·학습은 실행하지 않았다.
