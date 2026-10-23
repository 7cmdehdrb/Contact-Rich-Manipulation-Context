# Fusion v1_0 체크포인트 비교 이미지

[개발 로그](README.md) · [실행 기록](2026-10-23_fusion_v1_0_checkpoint_comparison.md)

**model_10000 vs model_16400(최신) · 각각 16환경 × 내부 시간 60초 · 중앙값 / 평균 / 최대값 및 분포**

[전체 이미지 한 장으로 보기](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/comparison_overview.png)

## 속도·가속도 분포

왼쪽은 구간별 표본 비율, 오른쪽은 해당 값 이하의 누적 비율입니다. 파란 실선은 model_10000, 주황 점선은 model_16400입니다.

### EEF 속도 분포

![EEF 속도 전체 분포](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/distribution_eef_speed.png)

### 물체 가속도 분포

활성 물체(타겟 포함)의 가속도 **0.01 m/s² 이상**을 사용합니다. 작은 값과 큰 값의 꼬리를 함께 보기 위해 가로축은 **로그 눈금**입니다.

![물체 가속도 전체 분포](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/distribution_object_acceleration.png)

### 환경별 EEF 속도 분포

![환경별 EEF 속도 분포](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/distribution_eef_speed_by_environment.png)

### 환경별 물체 가속도 분포

![환경별 물체 가속도 분포](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/distribution_object_acceleration_by_environment.png)

## EEF Linear Speed

![EEF Linear Speed 비교](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/comparison_eef_speed.png)

## 물체 접촉력 — 타겟 제외

![물체 접촉력 — 타겟 제외 비교](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/comparison_object_contact.png)

## 물체 가속도

![물체 가속도 비교](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/comparison_object_acceleration.png)

## RAW F/T 힘

![RAW F/T 힘 비교](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/comparison_raw_joint_force.png)

## RAW F/T 모멘트

![RAW F/T 모멘트 비교](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/comparison_raw_joint_moment.png)

## 장애물 전체 합력 — 페널티 입력

![장애물 전체 합력 — 페널티 입력 비교](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/comparison_obstacle_net.png)

## model10000 개별 이미지

<details>
<summary>model10000 이미지 펼치기</summary>

### EEF Linear Speed

![model10000 EEF Linear Speed](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model10000/eef_speed.png)

### 물체 접촉력 — 타겟 제외

![model10000 물체 접촉력 — 타겟 제외](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model10000/object_contact.png)

### 물체 가속도

![model10000 물체 가속도](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model10000/object_acceleration.png)

### RAW F/T 힘

![model10000 RAW F/T 힘](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model10000/raw_joint_force.png)

### RAW F/T 모멘트

![model10000 RAW F/T 모멘트](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model10000/raw_joint_moment.png)

### 장애물 전체 합력 — 페널티 입력

![model10000 장애물 전체 합력 — 페널티 입력](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model10000/obstacle_net.png)

### 보정 F/T 힘

![model10000 보정 F/T 힘](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model10000/penalty_eef_force.png)

### 보정 F/T 모멘트

![model10000 보정 F/T 모멘트](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model10000/penalty_eef_moment.png)

</details>

## model16400 개별 이미지

<details>
<summary>model16400 이미지 펼치기</summary>

### EEF Linear Speed

![model16400 EEF Linear Speed](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model16400/eef_speed.png)

### 물체 접촉력 — 타겟 제외

![model16400 물체 접촉력 — 타겟 제외](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model16400/object_contact.png)

### 물체 가속도

![model16400 물체 가속도](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model16400/object_acceleration.png)

### RAW F/T 힘

![model16400 RAW F/T 힘](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model16400/raw_joint_force.png)

### RAW F/T 모멘트

![model16400 RAW F/T 모멘트](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model16400/raw_joint_moment.png)

### 장애물 전체 합력 — 페널티 입력

![model16400 장애물 전체 합력 — 페널티 입력](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model16400/obstacle_net.png)

### 보정 F/T 힘

![model16400 보정 F/T 힘](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model16400/penalty_eef_force.png)

### 보정 F/T 모멘트

![model16400 보정 F/T 모멘트](../../03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/model16400/penalty_eef_moment.png)

</details>
