# Refactor 촉각 34채널 위치 재확인과 결정론적 4패널 그림

## 요청과 기존 그림의 오류

사용자가 손등 채널 23·26·29·32의 누락을 지적했고, 그럴듯한 생성 이미지가 아닌 실제 코드·모델의 위치로 손바닥·손등·엄지 양면을 합친 그림을 요청했다. 앞선 imagegen 결과는 정밀한 채널 위치 자료로 사용할 수 없다. 이전 기준 렌더도 영역들을 단순히 겹쳐 그렸고, 실제 코드의 중첩 영역 배정 규칙과 정확한 깊이 비교를 적용하지 않아 일부 영역이 가려졌다. 이전 두 그림은 보존하되 이 산출물로 대체한다.

## 실제 자료와 계산

`assets/scenes/wrench_refactor.py`가 참조하는 `assets/data/wrench_right_hand/ur5e_inspire_right.usda`를 USD Stage로 직접 열었다. 현재 합성된 `right_geometry`의 점과 각 body transform을 읽고 실제 collision approximation인 convexHull 표면을 재구성했다. 손 기본 프레임 기준으로 변환했으며 CAD 기본 펼침 자세다. 관절을 시뮬레이션 초기 자세나 학습된 자세로 움직인 화면은 아니다.

현재 오른손 `tactile_regions.json`의 17개 sensor XY footprint·parent hull과 `mdp/observation_functions/wrench_refactor.py::PairedContactRegions`를 기준으로 계산했다. 표면 픽셀별로 소유 body와 3D 위치·법선을 깊이 버퍼로 결정하고 footprint 허용오차 0.5mm 및 센서 Z법선 절댓값 0.2 조건을 적용했다. 중첩된 같은 parent의 후보들은 코드와 동일하게 센서 중심까지의 정규화 XY 거리 점수가 최소인 채널 하나에 배정했다. 실제 hull 표면 위에서는 외향 법선의 sensor Z성분 부호가 nearer upper/lower 판정과 대응한다. 직접 센서 body 접촉은 기존 front 채널로 표시했다.

## 23·26·29·32가 없어진 이유와 최종 표시

해당 채널은 삭제되지 않았다. 각각 검지·중지·약지·소지의 두 번째 front pad 6·9·12·15에 대응하는 back 채널이다. 세 번째 front pad 7·10·13·16의 back 채널 24·27·30·33과 거의 같은 손끝 위치로 투영된다. 실제 코드 배정 후에는 23·26·29·32가 큰 영역을 차지하고, 24·27·30·33은 작은 영역으로 남는다. 위치를 위아래로 임의 분리하지 않았다. 작은 영역은 진한 주황색과 실제 픽셀의 확대창으로 표시했다. 엄지 역시 앞면 1–4 / 반대면 18–21의 실제 중첩 배정을 적용했다.

4개 주 패널은 손바닥·손등·엄지 앞면·엄지 반대면이며 손등 패널 하단에 손끝 4쌍의 확대창이 있다. 번호 연결점은 해당 채널에 배정된 실제 렌더 표면 픽셀이다. 전체 손 시점에서 가려지는 엄지 2번과 21번은 하단 엄지 패널에서 표시한다. 어두운 회색의 손 표면은 시각 STL의 음영을 생성 모델로 정돈한 것이 아니라 실제 충돌 hull이다.

## 산출물과 검증

workspace `outputs/refactor_tactile_figure/`에 다음을 저장했다.

- `refactor_tactile_exact_four_panel.png`: 최종 통합 이미지, 3420×4140.
- `refactor_tactile_exact_four_panel.pdf`: 같은 그림의 PDF.
- `render_exact_four_panel.py`: 실제 USD를 읽는 결정론적 raster renderer.
- `verify_exact_regions.py`: 렌더 표면 샘플을 현재 소스의 실제 mapper로 검증.
- `exact_geometry_audit.json`: 패널별 실제 채널 픽셀 수·번호 연결점.
- `exact_runtime_validation.json`: 실제 mapper 대조 결과.
- `exact_panel_0_audit.npz`부터 `exact_panel_3_audit.npz`: 채널·3D 위치·body 인덱스 배열.

그림 전체에서 0–33의 모든 34채널이 실제 픽셀을 갖는 것을 assertion으로 검사했다. 최종 해상도에서 452개 표면 지점을 실제 소스에서 추출한 수정하지 않은 `PairedContactRegions` 및 Isaac Lab의 `quat_apply_inverse` 함수에 전달하여 452/452 일치를 확인했다. 직접 센서 body는 이 parent mapper 샘플 대조에서 제외했으며 해당 body의 채널 순서로 표시한다. 최종 그림과 손끝 확대창을 시각 확인했다. 생성형 이미지 도구는 사용하지 않았다.

환경 코드·원본 CAD·물리·PPO·학습 로그는 변경하지 않았다. 동적 접촉·힘 임계값·학습 성능은 검증 대상이 아니며 이번 그림은 기하학적 영역 배정의 시각화다.
