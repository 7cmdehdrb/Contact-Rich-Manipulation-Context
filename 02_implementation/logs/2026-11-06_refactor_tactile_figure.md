# Refactor 오른손 양면 촉각 영역 그림

정정: 이 생성형 그림의 손끝 채널 표시는 정밀 위치 자료로 사용할 수 없다. [실제 USD·코드 기반 34채널 4패널 그림](2026-11-06_refactor_tactile_exact_four_panel.md)으로 대체한다.

## 요청과 결과

사용자 요청은 최신 Refactor 환경의 실제 CAD를 참조하여 손바닥면과 손등면을 한 이미지에 표현하는 것이다. 기존 그림을 덮어쓰지 않고 workspace `outputs/refactor_tactile_figure/`에 새 산출물을 생성했다. 환경 코드·물리 자산·학습 설정과 학습 로그는 변경하지 않았다.

- `refactor_tactile_palm_dorsal.png`: built-in imagegen으로 CAD 기준 이미지를 정돈한 최종 설명용 그림.
- `cad_reference.png`: 원본 CAD 삼각형과 현재 메타데이터에서 직접 계산한 기준 렌더.
- `render_reference.py`: 원본 URDF/STL을 읽고 양면 영역을 계산하는 재현 스크립트.
- `prompt.txt`: 최종 생성에 사용한 전체 프롬프트.

## 근거와 대조

실제 Scene은 `assets/scenes/wrench_refactor.py`의 오른손 `wrench_right_hand/ur5e_inspire_right.usda`를 사용한다. 해당 자산을 만드는 `scripts/build_wrench_right_hand.py`와 `/tmp/inspire_urdf_right_with_force_sensor.zip`의 원본 URDF/STL을 확인했다. 원본 ZIP SHA256은 `b7997a6087e8c0cded03aff557e07ca82b8793b2b5b3f95ec3566318a13f5f7f`이며 현재 오른손 `tactile_regions.json`에 기록된 해시와 일치한다. 내부 `inspire_left_*` 명칭은 호환용 슬롯이며 그림의 형상은 오른손 원본이다.

`mdp/observation_functions/wrench_refactor.py::PairedContactRegions`에 따라 센서 로컬 XY 윤곽을 부모 convex hull의 upper/lower 표면에 투영했다. 앞면 0–16과 뒷면 17–33의 대응은 i와 i+17이다. 앞면은 청록색, 뒷면은 주황색으로 표시했으며 손등은 실제 센서 부품이 아닌 가상 투영 영역임을 그림 하단에 명시했다.

## 검증과 한계

재현 스크립트 실행 성공과 CAD 기준 렌더 및 생성 결과의 양면 구도·오른손 형상·색상·표제를 시각 확인했다. 시점은 펼친 CAD 자세이며 학습 중의 손 관절 자세를 재현한 것은 아니다. 측면 또는 가려진 일부 손끝/엄지 영역은 이 두 정면에서 면적이 작거나 보이지 않는다. 최종 그림은 생성 모델로 정돈한 설명용 그림으로서 경계의 정밀 측정이나 전체 34채널의 인덱스 판독에는 원본 메타데이터와 기준 렌더를 사용해야 한다. 특히 손등의 가려진 손끝 채널 23·26·29·32는 최종 그림에 별도 표시되지 않는다. GPU 물리·학습 검증은 수행하지 않았으며 이 그림 생성에는 필요하지 않다.
