# Final 영역 내부 물체 배치 설명 보완

- 요청: 영역 정의 이후 각 영역 안에서 물체 위치를 결정하는 규칙을 추가 설명한다.
- 대상: [장면 생성 문서](../../04_article/environment_reference/FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md)의 6.1.1–6.1.3절.
- 변경 전: 영역 정의와 전체 탐색 의사 코드는 있었으나, 영역 내부 직접 추출과 전체 선반 후보 거절 추출의 차이, OBB 경계 사례와 역할 유지 설명이 간략했다.
- 변경 후: yaw별 중심 범위 수식, 32개 위치·yaw 쌍, 첫 유효 후보 선택, Gray/White clearance 조건과 예시, 영역 간 공통 간격, 섞인 슬롯 순서, 중심 offset·바닥 높이 보정을 추가했다.
- 근거: `bbox_scene_layout.py`의 `generate_layout`, `zone_masks`, `separated`, `_sweep_clearance`와 `final_obb_geometry.py`의 `sample_shelf_layout`을 직접 확인했다.
- 최종 대조: Gray는 부분적인 근접 조건만으로 가능하며 White는 이를 제외한다. 역할 변경·후방 최소 수·격자·거리 최적화는 없다. 기존 32후보·4 restart·2 pass 및 실패 처리 설명은 보존했다.
- 영향: 설명 문서만 변경했다. 환경 코드·설정·기존 사용자 변경·학습 로그는 변경하지 않았다.
- 검증: 변경 문서 2개 수식 검사 통과. 전체 Markdown 429개 링크 오류 0건. 변경 문서 2개 외부 코드 링크 포함 검사 오류 0건. `git diff --check` 통과(기존 추적 파일의 LF/CRLF 안내만 출력). 추가 문구는 위 두 구현 파일과 직접 대조했다.
- 미검증 범위: 문서 보완 작업으로 시뮬레이터·학습을 새로 실행하지 않았으며, 새 성능·실행 결과를 주장하지 않는다.
