# 최신 Contact Formation 3D 시각화

## 요청과 범위

사용자가 최신 환경의 contact formulation을 Matplotlib으로 거리 x축, 각도 y축, 보상 z축의 3D plot으로 요청했다. 현재 인계와 실제 코드를 대조하여 Prof Revision v0_3_2를 대상으로 확정했다. 환경 코드, 계수, 상속, 학습 로그는 변경하지 않았다. 기존 사용자 변경도 보존했다.

## 확인한 수식과 의미

`mdp/common/prof_revision_geometry.py`의 `distance_angle_formation`은 손가락별 OBB 외부 거리와 각도 보상을 곱한 뒤 다섯 손가락을 합산한다. 각도는 지문면 로컬 +Z 법선과 현재 타깃 OBB 중심 방향 사이의 각도다. 거리는 중심 거리가 아니라 지문면 기준점에서 OBB까지의 거리이며 내부에서는 0이다. 양면을 허용하는 cos 제곱이므로 0도와180도에서 동일하고90도에서0이다. 유효하지 않은 법선/방향은0이다.

```math
c_i=\frac{0.05}{0.05+d_i}\cos^2\theta_i,\qquad
R_{\mathrm{step}}=0.1715\times0.02\times\sum_{i=1}^{5}c_i
```

거리 수식 단위는 m다. v0_3_2는 v0_3_1의 `distance_angle_sum` 모드와 기본 거리 척도0.05m를 상속한다. 가중치는0.1715이고 step dt는 decimation2 × sim dt0.01s=0.02s다. RewardManager의 weight × dt 적용도 실제 소스에서 확인했다.

## 추가 산출물과 영향

- [재현 스크립트](../../../../outputs/contact_formation_v0_3_2/plot_contact_formation.py)
- [PNG 그림](../../../../outputs/contact_formation_v0_3_2/contact_formation_3d.png)
- [SVG 그림](../../../../outputs/contact_formation_v0_3_2/contact_formation_3d.svg)

변경 전에는 해당 산출물이 없었고, 변경 후 독립적인 outputs 폴더에 시각화만 추가했다. 왼쪽은 한 손가락의 raw 기여, 오른쪽은 다섯 손가락의 거리와 각도가 모두 같은 단면의 가중 스텝 보상이다. 실제 환경은 각 손가락의 입력이 달라 일반적인 전체 보상은 단일 거리·각도의 함수가 아니다. 오른쪽 최대는0.01715/step이다. 표시는 거리0–20cm, 각도0–180도 범위다.

## 검증과 최종 대조

스크립트를 실행하여 PNG/SVG 생성에 성공했다. 실제 소스의 순수 Torch 함수를 AST로 추출해 실행하고29,141개 격자점에서 NumPy 수식과 절대오차1e-14 범위로 대조했다. 다섯 손가락 합산, 90도 영점, 각도 대칭, 최댓값과 finite 검사를 통과했다. 설정과 계수는 AST로 읽고 현재 계약과 일치함을 확인했다. PNG를 직접 열어 축·컬러바·수식·가정 문구의 배치를 확인했다.

검증 범위는 수식 시각화다. 실제 물리 장면의 도달 가능성, 학습 성능, GUI 회전 창 실행은 검증하지 않았다. `--show` 옵션으로 Matplotlib 회전 창을 열 수 있다. 기존 코드·환경·학습 로그 변경은 없다.
