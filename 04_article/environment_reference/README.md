# 최종 환경 설명 자료

이 폴더는 사용자 요청으로 작성한 최신 Final 환경 설명 문서를 모은다. 기준 환경은 `Isaac-Inspire-Final-GoalAccuracy-v0_2_2`이며, 각 문서에 적힌 작업트리 확인 날짜를 따른다. 구현 설명 자료이며 논문 최종 원고나 성능 검증 결과로 확정한 문서는 아니다.

| 문서 | 내용 |
| --- | --- |
| [초기 주변 물체 관측](FINAL_INITIAL_OBSTACLE_OBSERVATION.md) | 정면 가시성 근사·관측 제한의 이유·슬롯 마스크·좌표·정렬·노이즈 |
| [물체 구성과 무작위화 조건 표](FINAL_OBJECT_RANDOMIZATION_TABLES.md) | 종류·커리큘럼 최소/최대 수량·크기·질량·마찰 분포와 적용 시점 |
| [선반 작업 영역과 물체 형상](FINAL_SHELF_AND_OBJECT_GEOMETRY.md) | 작업면·경계·물체 치수·크기 변형·충돌 형상·역할 선택 |
| [Scene Generation and Randomization](FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md) | 대상·목표 생성, 배치 알고리즘, 실패 처리, 무작위화 시점 |
| [State and Privileged Information](FINAL_STATE_AND_PRIVILEGED_INFORMATION.md) | 환경 상태, Actor·Critic 관측, 좌표계·노이즈·부분 관측 |
| [학습 네트워크와 손실](FINAL_TRAINING_NETWORKS.md) | Actor·Critic·장애물 인코더 구조, PPO·GAE·손실 |
| [F/T 센서 형상과 Wrench 계측](FINAL_FT_SENSOR_AND_WRENCH.md) | 센서 치수, 고정 관절 반력, 좌표 변환, 중력·관성 보상 |

기존 환경별 구현 계약과 개발 로그는 [활성 환경 안내](../../02_implementation/08_ACTIVE_ENVIRONMENTS.md) 및 `02_implementation/logs`에서 관리한다. 촉각 센서 구성은 이 대화에서 별도 문서를 만들지 말라는 요청에 따라 독립 문서로 추가하지 않았다.
