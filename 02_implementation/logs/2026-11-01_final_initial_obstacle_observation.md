# 초기 주변 물체 관측 문서 작성

- 요청: 정면 가시성 판정, 보이는 물체만 포함하는 이유, 슬롯 마스크·좌표, 정렬·빈 슬롯·노이즈를 별도 문서로 정리한다.
- 산출물: [초기 주변 물체 관측](../../04_article/environment_reference/FINAL_INITIAL_OBSTACLE_OBSERVATION.md), 폴더 README 링크.
- 근거: Final reset의 `apply_final_visibility`와 compact reset, `classify_visibility_torch`, `pack_obstacle_observations`, 관측 캐시 반환 및 event 기본값을 확인했다.
- 주요 대조: 실제 위치로 가시성 판정, noisy 좌표로 정렬, 35% 투영 폭 기준, 1% 반전과 active mask, 10% 순차 인접 교환, 빈 슬롯 suffix 및 reset 고정을 설명했다. 타겟은 가림에 참여하지만 관측 슬롯에서는 제외한다.
- 한계: 비겹침 원 가정의 분류기에 OBB 외접 원을 전달하고 `check_inputs=False`로 호출하므로 실제 Final에서는 근사다. 실제 렌더링·높이 차이·로봇/선반 가림을 계산한다고 쓰지 않았다.
- 현재/예정: 현재 20슬롯과 요청된 16슬롯을 분리했다. 슬롯 변경은 미반영이며 코드·환경 동작·학습 로그는 변경하지 않았다.
- 검증: 변경 3문서 수식 검사 통과, 전체 Markdown 437개 링크 오류 0건, 새 설명 문서 외부 코드 링크 검사 오류 0건, `git diff --check` 통과(기존 LF/CRLF 안내만 출력). 새 시뮬레이터·학습·가시성 정확도 실험은 수행하지 않았다.
