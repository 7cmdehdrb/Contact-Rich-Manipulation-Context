# 환경 문서 안내

[구현 문서 안내](../README.md) · [등록·실행 안내](../08_ACTIVE_ENVIRONMENTS.md)

**[환경 계층과 변경 의도](ENVIRONMENT_EVOLUTION.md)부터 읽는다.** Baseline → Omni → Renewal과 Contact Sweep → Clutter → Fusion의 관계를 흐름도와 변경표로 확인하고, 전체 35개 등록 ID 표에서 개별 환경 문서로 이동할 수 있다. 실제 Python 상속과 기능을 가져와 독립 구성한 관계는 구분해서 표시했다.

| 찾는 내용 | 문서 |
| --- | --- |
| 전체 계층·부모에서 바꾼 이유·독립 문서 링크 | [환경 계층과 변경 의도](ENVIRONMENT_EVOLUTION.md) |
| Contact Sweep과 Clutter v0의 비교 | [Contact Sweep 환경 비교](CONTACT_SWEEP_ENVIRONMENTS.md) |
| Fusion v0 → v2 → v3 → v1_0 상세 변경 비교 | [Fusion 버전 비교](CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md) |
| 초기 Omni와 Dex의 접근·목표 수식 비교 | [보상 수식 비교](REACH_AND_GOAL_REWARD_FORMULAS.md) |
| 실제 실행 명령과 당시 검증 | [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md), [개발 로그](../logs/README.md) |

2026-10-22 추가한 간략 문서는 현재 코드 스냅샷을 설명한다. 기존 독립 문서는 유지했으며, 기록과 현재 코드의 차이는 [계층 문서의 읽기 기준](ENVIRONMENT_EVOLUTION.md#6-기록을-읽을-때의-기준)에 표시했다. 코드 링크는 상위 workspace와 함께 checkout한 경로를 기준으로 한다.

- [Fusion v1_1](CONTACT_SWEEP_CLUTTER_FUSION_V1_1_ENVIRONMENT.md): 초기 접촉 허용치와 지정 종료 시점 커리큘럼.
- [Fusion v1_2](CONTACT_SWEEP_CLUTTER_FUSION_V1_2_ENVIRONMENT.md): Goal 반경 2단계와 접촉 fade.

- [Fusion v1_1_1](CONTACT_SWEEP_CLUTTER_FUSION_V1_1_1_ENVIRONMENT.md): 장애물 힘·wrench 허용치 고정, 가속도 커리큘럼 실험.

- [Fusion v1_1_2](CONTACT_SWEEP_CLUTTER_FUSION_V1_1_2_ENVIRONMENT.md): 매우 큰 고정 가속도 기준과 장애물 힘·wrench 커리큘럼.

- [Fusion v1_3](CONTACT_SWEEP_CLUTTER_FUSION_V1_3_ENVIRONMENT.md): 힘·wrench·가속도 무료 기준의 point 기반 선형 커리큘럼.

- [Fusion v1_3_1](CONTACT_SWEEP_CLUTTER_FUSION_V1_3_1_ENVIRONMENT.md): Goal 반경과 접촉 fade width의 선형 커리큘럼.

- [Fusion v1_4](CONTACT_SWEEP_CLUTTER_FUSION_V1_4_ENVIRONMENT.md): v1_0 직접 상속, 250 간격 커리큘럼·최대 11개 물체·3초 목표 유지 성공 종료.
