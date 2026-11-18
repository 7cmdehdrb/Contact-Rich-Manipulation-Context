# 2026-11-14 압축 URDF 물리 파라미터 비교

## 요청·범위·해석

`outputs/data` 압축 파일의 Effort, Joint Velocity Limit, Mass, Inertia를 조회하고 차이를 비교했다. 원본 압축·환경 코드·학습 로그는 변경하지 않았다. 새 산출물은 조회 스크립트, 원시 설정 JSON과 이 비교표다.

상위 압축 3개와 중첩 압축을 합쳐 25개를 조회했다. URDF 13개, Xacro 11개이며, 바이트 중복을 제외한 URDF는 11개다. `RH56E2-R-T1.zip`에는 STEP 1개만 있고 URDF는 없다.

Effort 단위는 회전 관절 기준 N·m, velocity는 rad/s, mass는 kg, inertia는 kg·m²다. 모든 가동 관절은 revolute이며 mimic 관절도 포함한다. 합계 질량은 fixed 링크·센서·tip까지 포함한 URDF 선언값 합계다. 물리 장비 측정값이나 시뮬레이터의 최종 병합값을 뜻하지 않는다.

관성은 각 링크의 inertial 프레임에 선언된 6성분이다. 순서는 Ixx, Iyy, Izz, Ixy, Ixz, Iyz다. 서로 다른 링크의 관성을 합산하지 않았다. 좌우 프레임 차이로 비대각 성분의 부호가 달라질 수 있다. 아래 표는 10자리 유효숫자로 표시하고 JSON은 원문 수치 문자열 전체를 보존한다. 차이 판정은 허용오차 없이 Decimal 수치로 비교하며, 작은 CAD 정밀도 차이도 포함한다.

[전체 원시 설정·원점·출처 JSON](../../../../outputs/urdf_archive_comparison/parameters.json) · [재조회 스크립트](../../../../outputs/urdf_archive_comparison/inspect_archives.py)

## 모델별 요약

| 모델 | 링크 | 회전 관절 | Effort (N·m) | Velocity (rad/s) | 합계 질량 (kg) | 질량 0 링크 |
| --- | --- | --- | --- | --- | --- | --- |
| SDK force-sensor L | 30 | 12 | 10 | 1 | 0.87830 | 0 |
| RH56D/BFX L | 13 | 12 | 50 | 1 | 0.5392300000 | 0 |
| RH56D/BFX R | 13 | 12 | 50 | 1 | 0.5331644090 | 0 |
| RH56E2 L | 32 | 12 | 1 | 2 | 0.7836924599 | 0 |
| RH56E2 R | 32 | 12 | 1 | 1/2 | 0.7766626733 | 0 |
| RH56F1 L | 27 | 12 | 1 | 2 | 0.7077487661 | 10 |
| RH56F1 R | 27 | 12 | 1 | 2 | 0.7077487396 | 10 |
| RH56H1 L | 25 | 11 | 1 | 2 | 0.4139818441 | 0 |
| RH56H1 R | 25 | 11 | 1 | 2 | 0.4139704235 | 0 |
| RH5DG2 R | 27 | 18 | 1 | 2 | 0.5744532329 | 0 |
| RH5DG2 L | 27 | 18 | 1 | 2 | 0.5751956356 | 0 |

## 관절별 Effort·Velocity 차이

### SDK force-sensor L

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| fixed | 미지정 | 미지정 | palm_force_sensor_joint, thumb_force_sensor_1_joint, thumb_force_sensor_2_joint, thumb_force_sensor_3_joint, thumb_force_sensor_4_joint, index_force_sensor_1_joint, index_force_sensor_2_joint, index_force_sensor_3_joint, middle_force_sensor_1_joint, middle_force_sensor_2_joint, middle_force_sensor_3_joint, ring_force_sensor_1_joint, ring_force_sensor_2_joint, ring_force_sensor_3_joint, little_force_sensor_1_joint, little_force_sensor_2_joint, little_force_sensor_3_joint |
| revolute | 10 | 1 | left_thumb_1_joint, left_thumb_2_joint, left_thumb_3_joint, left_thumb_4_joint, left_index_1_joint, left_index_2_joint, left_middle_1_joint, left_middle_2_joint, left_ring_1_joint, left_ring_2_joint, left_little_1_joint, left_little_2_joint |

### RH56D/BFX L

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| revolute | 50 | 1 | left_thumb_1_joint, left_thumb_2_joint, left_thumb_3_joint, left_thumb_4_joint, left_index_1_joint, left_index_2_joint, left_middle_1_joint, left_middle_2_joint, left_ring_1_joint, left_ring_2_joint, left_little_1_joint, left_little_2_joint |

### RH56D/BFX R

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| revolute | 50 | 1 | right_thumb_1_joint, right_thumb_2_joint, right_thumb_3_joint, right_thumb_4_joint, right_index_1_joint, right_index_2_joint, right_middle_1_joint, right_middle_2_joint, right_ring_1_joint, right_ring_2_joint, right_little_1_joint, right_little_2_joint |

### RH56E2 L

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| revolute | 1 | 2 | left_thumb_1_joint, left_thumb_2_joint, left_thumb_3_joint, left_thumb_4_joint, left_index_1_joint, left_index_2_joint, left_middle_1_joint, left_middle_2_joint, left_ring_1_joint, left_ring_2_joint, left_little_1_joint, left_little_2_joint |
| fixed | 미지정 | 미지정 | left_thumb_force_sensor_2_joint, left_thumb_force_sensor_3_joint, left_thumb_force_sensor_4_joint, left_thumb_force_sensor_1_joint, left_index_force_sensor_2_joint, left_index_force_sensor_3_joint, left_index_force_sensor_1_joint, left_middle_force_sensor_2_joint, left_middle_force_sensor_3_joint, left_middle_force_sensor_1_joint, left_ring_force_sensor_2_joint, left_ring_force_sensor_3_joint, left_ring_force_sensor_1_joint, left_little_force_sensor_2_joint, left_little_force_sensor_3_joint, left_little_force_sensor_1_joint, left_plam_1_joint, left_plam_2_joint, left_plam_force_sensor_joint |

### RH56E2 R

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| fixed | 미지정 | 미지정 | right_plam_1_joint, right_plam_2_joint, right_plam_force_sensor_joint, right_thumb_force_sensor_2_joint, right_thumb_force_sensor_3_joint, right_thumb_force_sensor_4_joint, right_thumb_force_sensor_1_joint, right_index_force_sensor_2_joint, right_index_force_sensor_3_joint, right_index_force_sensor_1_joint, right_middle_force_sensor_2_joint, right_middle_force_sensor_3_joint, right_middle_force_sensor_1_joint, right_ring_force_sensor_2_joint, right_ring_force_sensor_3_joint, right_ring_force_sensor_1_joint, right_little_force_sensor_2_joint, right_little_force_sensor_3_joint, right_little_force_sensor_1_joint |
| revolute | 1 | 2 | right_thumb_1_joint, right_thumb_2_joint, right_thumb_3_joint, right_thumb_4_joint |
| revolute | 1 | 1 | right_index_1_joint, right_index_2_joint, right_middle_1_joint, right_middle_2_joint, right_ring_1_joint, right_ring_2_joint, right_little_1_joint, right_little_2_joint |

### RH56F1 L

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| revolute | 1 | 2 | left_thumb_1_joint, left_thumb_2_joint, left_thumb_3_joint, left_thumb_4_joint, left_index_1_joint, left_index_2_joint, left_middle_1_joint, left_middle_2_joint, left_ring_1_joint, left_ring_2_joint, left_little_1_joint, left_little_2_joint |
| fixed | 미지정 | 미지정 | thumb_force_sensor_joint, thumb_tip_joint, index_force_sensor_joint, index_tip_joint, middle_force_sensor_joint, middle_tip_joint, ring_force_sensor_joint, ring_tip_joint, little_force_sensor_joint, little_tip_joint, plam_1_joint, plam_2_joint, plam_3_joint, plam_force_sensor_joint |

### RH56F1 R

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| fixed | 미지정 | 미지정 | plam_1_joint, plam_2_joint, plam_3_jont, plam_force_sensor_joint, thumb_force_sensor_joint, thumb_tip_joint, index_force_sensor_joint, index_tip_joint, middle_force_sensor_joint, middle_tip_joint, ring_force_sensor_joint, ring_tip_joint, little_force_sensor_joint, little_tip_joint |
| revolute | 1 | 2 | right_thumb_1_joint, right_thumb_2_joint, right_thumb_3_joint, right_thumb_4_joint, right_index_1_joint, right_index_2_joint, right_middle_1_joint, right_middle_2_joint, right_ring_1_joint, right_ring_2_joint, right_little_1_joint, right_little_2_joint |

### RH56H1 L

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| fixed | 미지정 | 미지정 | left_hand_palm_joint, left_thumb_force_sensor_joint, left _thumb_tip_joint, left_index_force_sensor_joint, left_index_tip_joint, left_middle_force_sensor_joint, left_middle_tip_joint, left_ring_force_sensor_joint, left_ring_tip_joint, left_pinky_force_sensor_joint, left_pinky_tip_joint, left_palm_casing_joint, left_plam_force_sensor_joint |
| revolute | 1 | 2 | left_thumb_1_joint, left_thumb_2_joint, left_thumb_3_joint, left_index_1_joint, left_index_2_joint, left_middle_1_joint, left_middle_2_joint, left_ring_1_joint, left_ring_2_joint, left_pinky_1_joint, left_pinky_2_joint |

### RH56H1 R

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| fixed | 미지정 | 미지정 | right_hand_palm_joint, right_thumb_force_sensor_joint, right_thumb_tip_joint, right_index_force_sensor_joint, right_index_tip_joint, right_middle_force_sensor_joint, right_middle_tip_joint, right_ring_force_sensor_joint, right_ring_tip_joint, right_pinky_force_sensor_joint, right_pinky_tip_joint, right_palm_casing_joint, right_plam_force_sensor_joint |
| revolute | 1 | 2 | right_thumb_1_joint, right_thumb_2_joint, right_thumb_3_joint, right_index_1_joint, right_index_2_joint, right_middle_1_joint, right_middle_2_joint, right_ring_1_joint, right_ring_2_joint, right_pinky_1_joint, right_pinky_2_joint |

### RH5DG2 R

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| fixed | 미지정 | 미지정 | right_hand_palm_joint, right_thumb_force_sensor_joint, right_index_force_sensor_joint, right_middle_force_sensor_joint, right_ring_force_sensor_joint, right_pinky_force_sensor_joint |
| revolute | 1 | 2 | right_thumb_yaw_joint, right_thumb_mcp_joint, right_thumb_pip_joint, right_thumb_dip_joint, right_index_yaw_joint, right_index_mcp_joint, right_index_pip_joint, right_index_dip_joint, right_middle_yaw_joint, right_middle_mcp_joint, right_middle_pip_joint, right_middle_dip_joint, right_ring_mcp_joint, right_ring_pip_joint, right_ring_dip_joint, right_pinky_mcp_joint, right_pinky_pip_joint, right_pinky_dip_joint |
| fixed | 0 | 0 | right_palm_force_sensor_joint, right_hand_casing_joint |

### RH5DG2 L

| 종류 | Effort | Velocity | 관절 이름 |
| --- | --- | --- | --- |
| fixed | 미지정 | 미지정 | left_hand_palm_joint, left_thumb_force_sensor_joint, left_index_force_sensor_joint, left_middle_force_sensor_joint, left_ring_force_sensor_joint, left_pinky_force_sensor_joint |
| revolute | 1 | 2 | left_thumb_yaw_joint, left_thumb_mcp_joint, left_thumb_pip_joint, left_thumb_dip_joint, left_index_yaw_joint, left_index_mcp_joint, left_index_pip_joint, left_index_dip_joint, left_middle_yaw_joint, left_middle_mcp_joint, left_middle_pip_joint, left_middle_dip_joint, left_ring_mcp_joint, left_ring_pip_joint, left_ring_dip_joint, left_pinky_mcp_joint, left_pinky_pip_joint, left_pinky_dip_joint |
| fixed | 0 | 0 | left_palm_force_sensor_joint, left_hand_casing_joint |

fixed 관절의 미지정 값은 0으로 대체하지 않았다. RH5DG2의 palm_force_sensor_joint와 hand_casing_joint만 fixed이면서 effort=0, velocity=0을 명시한다.

## 좌우 대응 링크 비교

동일 계열 내 left_/right_/L_/R_ 접두사만 제거해 대응시켰다. 표의 관성 차이는 숫자가 다른 성분을 표시하며, 부호 차이와 미세한 차이를 모두 포함한다. 각 값은 뒤의 모델별 전체 표에서 확인할 수 있다.

### RH56D/BFX L / RH56D/BFX R

| 대응 링크 | L Mass (kg) | R Mass (kg) | 다른 Inertia 성분 |
| --- | --- | --- | --- |
| base_link | 0.38756 | 0.38756 | ixy, ixz, iyz |
| thumb_1 | 0.00483 | 0.00483 | ixy, ixz, iyz |
| thumb_2 | 0.05759 | 0.05759 | ixy, ixz, iyz |
| thumb_3 | 0.00985 | 0.003784408981 | ixy, ixz, iyz |
| thumb_4 | 0.00552 | 0.00552 | ixy, ixz, iyz |
| index_1 | 0.01229000000 | 0.01229 | ixy, ixz, iyz |
| index_2 | 0.00633 | 0.00633 | ixy, ixz, iyz |
| middle_1 | 0.01229000000 | 0.01229 | ixy, ixz, iyz |
| middle_2 | 0.006810000000 | 0.00681 | ixy |
| ring_1 | 0.01229000000 | 0.01229 | ixy, ixz, iyz |
| ring_2 | 0.00633 | 0.00633 | ixy, ixz, iyz |
| little_1 | 0.01229000000 | 0.01229000000 | ixy, ixz, iyz |
| little_2 | 0.00525 | 0.00525 | ixy |

합계 질량 L−R: 0.006065591019 kg.

### RH56E2 L / RH56E2 R

| 대응 링크 | L Mass (kg) | R Mass (kg) | 다른 Inertia 성분 |
| --- | --- | --- | --- |
| base_link | 0.090 | 0.090 | ixy, iyz |
| thumb_1 | 0.01537 | 0.01537 | ixy, iyz |
| thumb_2 | 0.1103400000 | 0.1103400000 | ixy, iyz |
| thumb_3 | 0.01779 | 0.01779 | ixy, iyz |
| thumb_force_sensor_2 | 0.0001190242360 | 0.0001190241979 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_4 | 0.00766 | 0.00766 | ixy, iyz |
| thumb_force_sensor_3 | 0.0001698941760 | 0.0001698938324 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_force_sensor_4 | 0.00001669910742 | 0.00001669912051 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_force_sensor_1 | 0.0002343515224 | 0.0002343458706 | ixx, iyy, izz, ixy, ixz, iyz |
| index_1 | 0.01869000000 | 0.01869000000 | ixy, iyz |
| index_2 | 0.01102 | 0.01102 | ixy, iyz |
| index_force_sensor_2 | 0.0002557481935 | 0.0002557484582 | ixx, iyy, izz, ixy, ixz, iyz |
| index_force_sensor_3 | 0.00006796539026 | 0.00006796469849 | ixx, iyy, izz, ixy, ixz, iyz |
| index_force_sensor_1 | 0.00020279 | 0.0002027792621 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_1 | 0.01866 | 0.01866 | ixy, iyz |
| middle_2 | 0.01767 | 0.01767 | ixy, iyz |
| middle_force_sensor_2 | 0.0002625735939 | 0.0002625933144 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_force_sensor_3 | 0.00006649142729 | 0.00006649145755 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_force_sensor_1 | 0.0002027945221 | 0.0002027793883 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_1 | 0.01869000000 | 0.01869000000 | ixy, iyz |
| ring_2 | 0.01102 | 0.01102 | ixy, iyz |
| ring_force_sensor_2 | 0.0002557481909 | 0.0002557484556 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_force_sensor_3 | 0.00006796576346 | 0.00006796503922 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_force_sensor_1 | 0.0002027944344 | 0.0002027792234 | ixx, iyy, izz, ixy, ixz, iyz |
| little_1 | 0.01869000000 | 0.01869000000 | ixy, iyz |
| little_2 | 0.01869000000 | 0.01166 | ixx, iyy, izz, ixy, ixz, iyz |
| little_force_sensor_2 | 0.0002802467485 | 0.0002802653638 | ixx, iyy, izz, ixy, ixz, iyz |
| little_force_sensor_3 | 0.00006105366701 | 0.00006105399217 | ixx, iyy, izz, ixy, ixz, iyz |
| little_force_sensor_1 | 0.0002027945023 | 0.0002027792902 | ixx, iyy, izz, ixy, ixz, iyz |
| plam_1 | 0.38382 | 0.38382 | ixy, iyz |
| plam_2 | 0.02050465891 | 0.02050488395 | ixx, iyy, izz, ixy, ixz, iyz |
| plam_force_sensor | 0.002408865563 | 0.002408878383 | ixx, iyy, izz, ixy, ixz, iyz |

합계 질량 L−R: 0.007029786642 kg.

### RH56F1 L / RH56F1 R

| 대응 링크 | L Mass (kg) | R Mass (kg) | 다른 Inertia 성분 |
| --- | --- | --- | --- |
| base_link | 0.07939453394 | 0.07939450036 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_1 | 0.01680000000 | 0.01680000000 | ixy, iyz |
| thumb_2 | 0.06526 | 0.06526 | ixy, iyz |
| thumb_3 | 0.01333 | 0.01333 | ixy, iyz |
| thumb_4 | 0.01144000000 | 0.01144000000 | ixy |
| index_1 | 0.01111 | 0.01111 | ixy, iyz |
| index_2 | 0.0103 | 0.0103 | ixy, iyz |
| middle_1 | 0.01111 | 0.01111 | ixy, iyz |
| middle_2 | 0.01122 | 0.01122 | ixy, iyz |
| ring_1 | 0.01111 | 0.01111 | ixy, iyz |
| ring_2 | 0.0103 | 0.0103 | ixy, iyz |
| little_1 | 0.01111 | 0.01111 | ixy, iyz |
| little_2 | 0.00839 | 0.00839 | ixy, iyz |
| plam_1 | 0.41238 | 0.41238 | ixy, iyz |
| plam_2 | 0.01 | 0.01 | ixx, iyy, izz, ixy, ixz, iyz |
| plam_3 | 0.01 | 0.01 | ixx, iyy, izz, ixy, ixz, iyz |
| plam_force_sensor | 0.004494232135 | 0.004494239271 | ixx, iyy, izz, ixy, ixz, iyz |

합계 질량 L−R: 2.644187831e-8 kg.

### RH56H1 L / RH56H1 R

| 대응 링크 | L Mass (kg) | R Mass (kg) | 다른 Inertia 성분 |
| --- | --- | --- | --- |
| hand_base | 0.02984970410 | 0.02984965117 | ixx, iyy, izz, ixy, ixz, iyz |
| hand_palm | 0.2259755564 | 0.2259703473 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_1 | 0.004887759577 | 0.004887759577 | ixx, iyy, ixy, ixz, iyz |
| thumb_2 | 0.04587452022 | 0.04587288317 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_3 | 0.01363616663 | 0.01363671154 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_force_sensor | 0.001055981151 | 0.001056012723 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_tip | 2.218622838e-7 | 2.220619608e-7 | ixx, iyy, izz, ixy, ixz, iyz |
| index_1 | 0.006299680764 | 0.006300135061 | ixx, iyy, izz, ixy, ixz, iyz |
| index_2 | 0.01148120993 | 0.01148137229 | ixx, iyy, izz, ixy, ixz, iyz |
| index_force_sensor | 0.001406457153 | 0.001406334256 | ixx, iyy, izz, ixy, ixz, iyz |
| index_tip | 1.916750079e-7 | 1.918574337e-7 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_1 | 0.006299685155 | 0.006300166403 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_2 | 0.01204640205 | 0.01204626026 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_force_sensor | 0.001406455454 | 0.001406334056 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_tip | 1.916775962e-7 | 1.918551362e-7 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_1 | 0.006299666700 | 0.006300151241 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_2 | 0.01148130488 | 0.01148153146 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_force_sensor | 0.001406455248 | 0.001406338171 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_tip | 1.916750390e-7 | 1.918569107e-7 | ixx, iyy, izz, ixy, ixz, iyz |
| pinky_1 | 0.006299675571 | 0.006300153361 | ixx, iyy, izz, ixy, ixz, iyz |
| pinky_2 | 0.009044444614 | 0.009044247927 | ixx, iyy, izz, ixy, ixz, iyz |
| pinky_force_sensor | 0.001406454496 | 0.001406338380 | ixx, iyy, izz, ixy, ixz, iyz |
| pinky_tip | 1.916732782e-7 | 1.918577176e-7 | ixx, iyy, izz, ixy, ixz, iyz |
| palm_casing | 0.01601980776 | 0.01601339194 | ixx, iyy, izz, ixy, ixz, iyz |
| plam_force_sensor | 0.001803467651 | 0.001803313808 | ixx, iyy, izz, ixy, ixz, iyz |

합계 질량 L−R: 0.00001142052998 kg.

### RH5DG2 L / RH5DG2 R

| 대응 링크 | L Mass (kg) | R Mass (kg) | 다른 Inertia 성분 |
| --- | --- | --- | --- |
| hand_base | 0.08162724319 | 0.08162727654 | ixx, iyy, izz, ixy, ixz, iyz |
| hand_palm | 0.2616711202 | 0.2611098889 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_yaw | 0.004817398943 | 0.004817354503 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_mcp | 0.04175584871 | 0.04175607115 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_pip | 0.04138153842 | 0.04138096334 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_dip | 0.007376477044 | 0.007376361360 | ixx, iyy, izz, ixy, ixz, iyz |
| thumb_force_sensor | 0.0008557718313 | 0.0008215441274 | ixx, iyy, izz, ixy, ixz, iyz |
| index_yaw | 0.001534984468 | 0.001534984468 | ixx, iyy, izz, ixy, ixz, iyz |
| index_mcp | 0.01282476886 | 0.01282476912 | ixx, iyy, izz, ixy, ixz, iyz |
| index_pip | 0.005744752521 | 0.005744746475 | ixx, iyy, izz, ixy, ixz, iyz |
| index_dip | 0.006649827639 | 0.006649773227 | ixx, iyy, izz, ixy, ixz, iyz |
| index_force_sensor | 0.0008557598683 | 0.0008215234364 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_yaw | 0.001534984468 | 0.001534984468 | iyy, izz, ixy, ixz, iyz |
| middle_mcp | 0.01282476826 | 0.01282476885 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_pip | 0.005744752471 | 0.005744746420 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_dip | 0.007909089008 | 0.007909026292 | ixx, iyy, izz, ixy, ixz, iyz |
| middle_force_sensor | 0.0008557597515 | 0.0008215236267 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_mcp | 0.01268412184 | 0.01268412256 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_pip | 0.005744752489 | 0.005744746577 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_dip | 0.007518906854 | 0.007518951815 | ixx, iyy, izz, ixy, ixz, iyz |
| ring_force_sensor | 0.0008557598402 | 0.0008215237684 | ixx, iyy, izz, ixy, ixz, iyz |
| pinky_mcp | 0.01268412185 | 0.01268412274 | ixx, iyy, izz, ixy, ixz, iyz |
| pinky_pip | 0.005744752481 | 0.005744746474 | ixx, iyy, izz, ixy, ixz, iyz |
| pinky_dip | 0.006398736864 | 0.006398790742 | ixx, iyy, izz, ixy, ixz, iyz |
| pinky_force_sensor | 0.0008557589536 | 0.0008215230643 | ixx, iyy, izz, ixy, ixz, iyz |
| palm_force_sensor | 0.005102714649 | 0.005102735173 | ixx, iyy, izz, ixy, ixz, iyz |
| hand_casing | 0.02164116409 | 0.02163166363 | ixx, iyy, izz, ixy, ixz, iyz |

합계 질량 L−R: 0.0007424026862 kg.

## 모델별 전체 링크 Mass·Inertia

### SDK force-sensor L

robot name: `urdf_left_with_force_sensor`.

출처: `outputs/data/SDK.zip!SDK/ros2.rar!ros2/四代手控制程序/inspire_hand_Linkage.zip!src/urdf_left_with_force_sensor/urdf/urdf_left_with_force_sensor.urdf`.
출처: `outputs/data/SDK.zip!SDK/ros2.rar!ros2/四代手控制程序/仿真+硬件联合驱动/inspire_hand_Linkage.zip!src/urdf_left_with_force_sensor/urdf/urdf_left_with_force_sensor.urdf`.
출처: `outputs/data/SDK.zip!SDK/urdf.rar!src/urdf_left_with_force_sensor/urdf/urdf_left_with_force_sensor.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base_link | 0.62266 | 0.0002213078237 | 0.0002651345478 | 0.0001323113857 | 0.000001164907482 | -5.803253062e-7 | 0.00001551875210 |
| palm_force_sensor | 0.001 | 1.792378474e-7 | 5.018873248e-7 | 6.800172377e-7 | -3.623352510e-10 | 2.068388297e-10 | -4.235370576e-10 |
| left_thumb_1 | 0.00746 | 1.298351987e-7 | 1.112220491e-7 | 7.034005997e-8 | 5.711602093e-9 | -1.487589837e-8 | -2.105208978e-9 |
| left_thumb_2 | 0.04264 | 0.000001069926207 | 9.941798955e-7 | 0.000001350953701 | 7.738952816e-8 | -1.823000784e-9 | -2.147685952e-9 |
| thumb_force_sensor_1 | 0.001 | 9.011220657e-9 | 4.945579644e-9 | 1.356513428e-8 | 2.066734013e-14 | -2.311984729e-12 | -1.178923036e-11 |
| left_thumb_3 | 0.01501 | 5.195531484e-7 | 5.033867255e-7 | 5.336243327e-7 | 1.004090556e-7 | -1.222605123e-10 | 2.625271919e-11 |
| thumb_force_sensor_2 | 0.001 | 3.347482963e-10 | 3.358216491e-10 | 5.885784703e-10 | 3.773587361e-14 | -3.522737232e-13 | -1.089649394e-12 |
| left_thumb_4 | 0.00972 | 5.948972064e-7 | 7.792023494e-7 | 8.998241901e-7 | 2.542513619e-7 | 5.540859922e-11 | 8.896511198e-11 |
| thumb_force_sensor_3 | 0.001 | 5.411734903e-9 | 2.558960799e-9 | 7.827646248e-9 | -4.877004479e-13 | 6.300246794e-13 | -3.823514683e-11 |
| thumb_force_sensor_4 | 0.001 | 8.135788988e-11 | 1.707785312e-10 | 2.116442623e-10 | -2.555163199e-14 | -2.015208960e-14 | 3.772242729e-12 |
| left_index_1 | 0.02841 | 0.000001131529585 | 5.502741014e-7 | 0.000001174744302 | 7.343208146e-8 | -7.015928549e-12 | -5.175378678e-11 |
| index_force_sensor_1 | 0.001 | 3.380624989e-9 | 1.964252055e-9 | 5.281295941e-9 | 5.068780205e-11 | 2.188959735e-13 | -5.526264086e-12 |
| left_index_2 | 0.01218 | 0.000002111522308 | 3.704676792e-7 | 0.000002143569717 | 3.783785903e-7 | 4.180439826e-10 | -2.787057927e-9 |
| index_force_sensor_2 | 0.001 | 4.798776817e-9 | 2.439579539e-9 | 7.125684637e-9 | 8.641895852e-11 | 1.504218028e-12 | -3.051644048e-11 |
| index_force_sensor_3 | 0.001 | 1.319760817e-10 | 2.534344707e-10 | 2.805368970e-10 | -5.650979896e-12 | -7.801099147e-13 | 9.121746251e-12 |
| left_middle_1 | 0.02841 | 0.000001131529611 | 5.502741068e-7 | 0.000001174744335 | 7.343208031e-8 | -7.009007324e-12 | -5.174666749e-11 |
| middle_force_sensor_1 | 0.001 | 3.382436219e-9 | 1.962441279e-9 | 5.281296366e-9 | 2.846147112e-14 | 2.155816632e-14 | -5.530359666e-12 |
| left_middle_2 | 0.01561 | 0.000002586580455 | 4.103273473e-7 | 0.000002629542900 | 4.532627102e-7 | 5.551075062e-12 | -8.437412662e-12 |
| middle_force_sensor_2 | 0.001 | 5.041487659e-9 | 2.567779879e-9 | 7.494578373e-9 | 1.870531807e-13 | -1.921983999e-14 | 3.471505996e-12 |
| middle_force_sensor_3 | 0.001 | 1.272277162e-10 | 2.436910209e-10 | 2.758750290e-10 | -8.966436759e-15 | -8.771047989e-15 | 7.612765415e-12 |
| left_ring_1 | 0.02841 | 0.000001131529308 | 5.502740930e-7 | 0.000001174743966 | 7.343203939e-8 | -7.098303984e-12 | -5.181120017e-11 |
| ring_force_sensor_1 | 0.001 | 3.378370112e-9 | 1.966506183e-9 | 5.281295219e-9 | -7.587875297e-11 | -2.745804246e-13 | -5.523931381e-12 |
| left_ring_2 | 0.01281 | 0.000002111523349 | 3.704679465e-7 | 0.000002143570849 | 3.783787729e-7 | 4.176461015e-10 | -2.789282384e-9 |
| ring_force_sensor_2 | 0.001 | 4.794452470e-9 | 2.443903568e-9 | 7.125684197e-9 | -1.328564425e-10 | -1.331380929e-12 | -3.052450979e-11 |
| ring_force_sensor_3 | 0.001 | 1.322695535e-10 | 2.531442269e-10 | 2.805397917e-10 | 8.210097551e-12 | 2.628817220e-13 | 9.150969484e-12 |
| left_little_1 | 0.02841 | 0.000001131528961 | 5.502740692e-7 | 0.000001174743541 | 7.343200088e-8 | -7.199633103e-12 | -5.188801336e-11 |
| little_force_sensor_1 | 0.001 | 3.366216104e-9 | 1.978661564e-9 | 5.281296553e-9 | -1.508960824e-10 | -5.697736882e-13 | -5.501057524e-12 |
| left_little_2 | 0.00957 | 0.000001146914277 | 2.661711269e-7 | 0.000001150542329 | 2.222363300e-7 | -2.329879031e-11 | 2.778934201e-11 |
| little_force_sensor_2 | 0.001 | 5.360447391e-9 | 2.788808434e-9 | 8.009574740e-9 | -2.903837672e-10 | 4.212504704e-12 | 3.605596839e-11 |
| little_force_sensor_3 | 0.001 | 1.115915963e-10 | 2.172065347e-10 | 2.520523052e-10 | 1.489232869e-11 | 1.182944923e-12 | 8.078835709e-12 |

### RH56D/BFX L

robot name: `urdf_left_2025_4_22`.

출처: `outputs/data/URDF.zip!URDF/RH56D,BFX/urdf_left.zip!urdf_left_2025_4_22/urdf/urdf_left_2025_4_22.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L_base_link | 0.38756 | 0.00059831308 | 0.00050077156 | 0.00018467082 | -0.00000560829 | -0.000002870140000 | -0.000003483100000 |
| left_thumb_1 | 0.00483 | 1.9502e-7 | 1.4336e-7 | 1.6891e-7 | 3.536e-8 | 3.1e-9 | 7.9e-9 |
| left_thumb_2 | 0.05759 | 0.00001066621000 | 0.00000892353 | 0.00001700133 | 0.000004413610000 | 5.150000000e-9 | -2.59e-9 |
| left_thumb_3 | 0.00985 | 0.00000121069 | 6.011800000e-7 | 0.00000128966 | 1.0767e-7 | 1.000000000e-11 | 3e-11 |
| left_thumb_4 | 0.00552 | 3.1668e-7 | 1.299900000e-7 | 3.3747e-7 | 4.536e-8 | -1.000000000e-11 | -4e-10 |
| left_index_1 | 0.01229000000 | 0.00000193998 | 5.6245e-7 | 0.00000205872 | 1.5035e-7 | 4.1e-10 | 3.49e-9 |
| left_index_2 | 0.00633 | 9.4327e-7 | 2.897e-7 | 0.00000114024 | 3.8912e-7 | 2.000000000e-11 | 5e-11 |
| left_middle_1 | 0.01229000000 | 0.00000194 | 5.6248e-7 | 0.00000205872 | 1.5036e-7 | 9.900000000e-10 | 5.01e-9 |
| left_middle_2 | 0.006810000000 | 0.00000118348 | 3.558e-7 | 0.00000143878 | 5.0397e-7 | 0.0 | 0.0 |
| left_ring_1 | 0.01229000000 | 0.00000193998 | 5.6244e-7 | 0.00000205872 | 1.503300000e-7 | 5.1e-10 | 3.52e-9 |
| left_ring_2 | 0.00633 | 9.4329e-7 | 2.961500000e-7 | 0.00000113377 | 3.8762e-7 | 3.394e-8 | 7.389e-8 |
| left_little_1 | 0.01229000000 | 0.00000194 | 5.624200000e-7 | 0.00000205872 | 1.5023e-7 | 3e-10 | 3.18e-9 |
| left_little_2 | 0.00525 | 5.5787e-7 | 1.8624e-7 | 6.690600000e-7 | 2.175e-7 | 0.0 | 0.0 |

### RH56D/BFX R

robot name: `urdf_right_2025_4_18`.

출처: `outputs/data/URDF.zip!URDF/RH56D,BFX/urdf_right.zip!urdf_right_2025_4_18/urdf/urdf_right_2025_4_18.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R_base_link | 0.38756 | 0.00059831308 | 0.00050077156 | 0.00018467082 | 0.00000560829 | 0.000002870140000 | 0.000003483100000 |
| right_thumb_1 | 0.00483 | 1.9502e-7 | 1.4336e-7 | 1.6891e-7 | -3.536e-8 | -3.1e-9 | -7.9e-9 |
| right_thumb_2 | 0.05759 | 0.00001066621000 | 0.00000892353 | 0.00001700133 | -0.000004413610000 | -5.150000000e-9 | 2.59e-9 |
| right_thumb_3 | 0.003784408981 | 0.00000121069 | 6.011800000e-7 | 0.00000128966 | -1.0767e-7 | -1.000000000e-11 | -3e-11 |
| right_thumb_4 | 0.00552 | 3.1668e-7 | 1.299900000e-7 | 3.3747e-7 | -4.536e-8 | 1.000000000e-11 | 4e-10 |
| right_index_1 | 0.01229 | 0.00000193998 | 5.6245e-7 | 0.00000205872 | -1.5035e-7 | -4.1e-10 | -3.49e-9 |
| right_index_2 | 0.00633 | 9.4327e-7 | 2.897e-7 | 0.00000114024 | -3.8912e-7 | -2.000000000e-11 | -5e-11 |
| right_middle_1 | 0.01229 | 0.00000194 | 5.6248e-7 | 0.00000205872 | -1.5036e-7 | -9.900000000e-10 | -5.01e-9 |
| right_middle_2 | 0.00681 | 0.00000118348 | 3.558e-7 | 0.00000143878 | -5.0397e-7 | -0.0 | -0.0 |
| right_ring_1 | 0.01229 | 0.00000193998 | 5.6244e-7 | 0.00000205872 | -1.503300000e-7 | -5.1e-10 | -3.52e-9 |
| right_ring_2 | 0.00633 | 9.4329e-7 | 2.961500000e-7 | 0.00000113377 | -3.8762e-7 | -3.394e-8 | -7.389e-8 |
| right_little_1 | 0.01229000000 | 0.00000194 | 5.624200000e-7 | 0.00000205872 | -1.5023e-7 | -3e-10 | -3.18e-9 |
| right_little_2 | 0.00525 | 5.5787e-7 | 1.8624e-7 | 6.690600000e-7 | -2.175e-7 | -0.0 | -0.0 |

### RH56E2 L

robot name: `RH56E2_L_2025_9_10`.

출처: `outputs/data/URDF.zip!URDF/RH56E2 URDF.zip!RH56E2_L_2025_9_10/urdf/RH56E2_L_2025_9_10.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base_link | 0.090 | 0.00002786853809 | 0.00002678053934 | 0.00003648867670 | -4.781395049e-11 | -3.964659153e-8 | -1.058350263e-11 |
| left_thumb_1 | 0.01537 | 9.7931e-7 | 6.735400000e-7 | 8.6359e-7 | 6.197e-8 | -4.9e-9 | 3.629000000e-8 |
| left_thumb_2 | 0.1103400000 | 0.00001996898 | 0.00003366305 | 0.00004234759000 | -0.00001123516 | -0.00000396656 | -0.00000122531 |
| left_thumb_3 | 0.01779 | 0.00000309353 | 0.00000257591 | 0.00000332754 | -3.912100000e-7 | 1.293000000e-8 | 7.61e-9 |
| left_thumb_force_sensor_2 | 0.0001190242360 | 1.022451468e-9 | 9.970389534e-10 | 1.990651455e-9 | -6.722405015e-13 | -1.142408851e-12 | -8.163792116e-12 |
| left_thumb_4 | 0.00766 | 0.00000115326 | 5.7535e-7 | 0.00000115929 | -1.6573e-7 | -4.000000000e-11 | 7e-11 |
| left_thumb_force_sensor_3 | 0.0001698941760 | 3.916955636e-9 | 1.418834372e-9 | 5.295248349e-9 | -3.848813692e-15 | 2.568320474e-13 | -1.729567407e-10 |
| left_thumb_force_sensor_4 | 0.00001669910742 | 2.257733278e-11 | 2.307744175e-11 | 4.316372808e-11 | 2.523630084e-15 | -5.300055849e-15 | 1.744068336e-13 |
| left_thumb_force_sensor_1 | 0.0002343515224 | 6.825854591e-9 | 2.917206967e-9 | 9.689204153e-9 | 1.333305358e-11 | -9.240674126e-12 | -1.796921532e-10 |
| left_index_1 | 0.01869000000 | 0.00000359962 | 0.00000120603 | 0.00000379687 | 4.164600000e-7 | -1.660000000e-9 | 6.3e-10 |
| left_index_2 | 0.01102 | 0.00000232185 | 4.134e-7 | 0.000002423840000 | 5.6428e-7 | 9e-11 | -3.9e-10 |
| left_index_force_sensor_2 | 0.0002557481935 | 7.125684637e-9 | 2.439579539e-9 | 4.798776817e-9 | -3.051644051e-11 | -1.504218029e-12 | -8.641895852e-11 |
| left_index_force_sensor_3 | 0.00006796539026 | 1.319760803e-10 | 2.534344658e-10 | 2.805368915e-10 | -5.650977771e-12 | -7.801086787e-13 | 9.121746806e-12 |
| left_index_force_sensor_1 | 0.00020279 | 3.3806e-9 | 1.9643e-9 | 5.2813e-9 | 5.0688e-11 | 2.189e-13 | -5.5263e-12 |
| left_middle_1 | 0.01866 | 0.00000359341 | 0.00000120028 | 0.000003785240000 | 4.005900000e-7 | -1.64e-9 | 1.21e-9 |
| left_middle_2 | 0.01767 | 0.00000463728 | 9.821e-7 | 0.00000500365 | 0.00000135163 | 2.92e-9 | -1.151e-8 |
| left_middle_force_sensor_2 | 0.0002625735939 | 5.041487659e-9 | 2.567779879e-9 | 7.494578373e-9 | 1.870531807e-13 | -1.921984000e-14 | 3.471505966e-12 |
| left_middle_force_sensor_3 | 0.00006649142729 | 1.272277162e-10 | 2.436910209e-10 | 2.758750290e-10 | -8.966436757e-15 | -8.771047985e-15 | 7.612765415e-12 |
| left_middle_force_sensor_1 | 0.0002027945221 | 3.382436219e-9 | 1.962441279e-9 | 5.281296366e-9 | 2.846147113e-14 | 2.155816630e-14 | -5.530359681e-12 |
| left_ring_1 | 0.01869000000 | 0.00000360961 | 0.00000120307 | 0.00000378952 | 3.8725e-7 | -2.195000000e-8 | 1.3659e-7 |
| left_ring_2 | 0.01102 | 0.000002347110000 | 3.9493e-7 | 0.00000241823 | 5.196000000e-7 | -2.702e-8 | 1.066800000e-7 |
| left_ring_force_sensor_2 | 0.0002557481909 | 4.794452470e-9 | 2.443903568e-9 | 7.125684197e-9 | -1.328564425e-10 | -1.331380926e-12 | -3.052450974e-11 |
| left_ring_force_sensor_3 | 0.00006796576346 | 1.322695538e-10 | 2.531442285e-10 | 2.805397934e-10 | 8.210096928e-12 | 2.628814918e-13 | 9.150969392e-12 |
| left_ring_force_sensor_1 | 0.0002027944344 | 3.378370112e-9 | 1.966506183e-9 | 5.281295219e-9 | -7.587875297e-11 | -2.745804232e-13 | -5.523931356e-12 |
| left_little_1 | 0.01869000000 | 0.000003634640000 | 0.00000119929 | 0.00000376746 | 3.0236e-7 | -3.342000000e-8 | 2.7369e-7 |
| left_little_2 | 0.01869000000 | 0.000003634640000 | 0.00000119929 | 0.00000376746 | 3.0236e-7 | -3.342000000e-8 | 2.7369e-7 |
| left_little_force_sensor_2 | 0.0002802467485 | 5.360447391e-9 | 2.788808434e-9 | 8.009574740e-9 | -2.903837672e-10 | 4.212504713e-12 | 3.605596847e-11 |
| left_little_force_sensor_3 | 0.00006105366701 | 1.115915963e-10 | 2.172065347e-10 | 2.520523052e-10 | 1.489232869e-11 | 1.182944923e-12 | 8.078835709e-12 |
| left_little_force_sensor_1 | 0.0002027945023 | 3.366216104e-9 | 1.978661564e-9 | 5.281296553e-9 | -1.508960824e-10 | -5.697736850e-13 | -5.501057494e-12 |
| left_plam_1 | 0.38382 | 0.00054913744 | 0.00040036048 | 0.00022521596 | 0.00000442438 | 0.00002985901000 | -0.000009570770000 |
| left_plam_2 | 0.02050465891 | 0.00002376710484 | 0.00001278430406 | 0.00001203517293 | -1.290725752e-8 | -6.437644799e-8 | 9.829077162e-8 |
| left_plam_force_sensor | 0.002408865563 | 1.792378474e-7 | 5.018873248e-7 | 6.800172377e-7 | -3.623352510e-10 | 2.068388297e-10 | -4.235370576e-10 |

### RH56E2 R

robot name: `RH56E2_R_2025_9_11`.

출처: `outputs/data/URDF.zip!URDF/RH56E2 URDF.zip!RH56E2_R_2025_9_11/urdf/RH56E2_R_2025_9_11.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base_link | 0.090 | 0.00002786853809 | 0.00002678053934 | 0.00003648867670 | 4.781395049e-11 | -3.964659153e-8 | 1.058350263e-11 |
| right_plam_1 | 0.38382 | 0.00054913744 | 0.00040036048 | 0.00022521596 | -0.00000442438 | 0.00002985901000 | 0.000009570770000 |
| right_plam_2 | 0.02050488395 | 0.00002376730544 | 0.00001278065310 | 0.00001203883977 | -1.165646994e-8 | -5.545907757e-8 | 1.113754077e-7 |
| right_plam_force_sensor | 0.002408878383 | 1.792409882e-7 | 5.019252832e-7 | 6.800583132e-7 | 3.529758518e-10 | -2.060081065e-10 | -4.233110431e-10 |
| right_thumb_1 | 0.01537 | 9.7931e-7 | 6.735400000e-7 | 8.6359e-7 | -6.197e-8 | -4.9e-9 | -3.629000000e-8 |
| right_thumb_2 | 0.1103400000 | 0.00001996898 | 0.00003366305 | 0.00004234759000 | 0.00001123516 | -0.00000396656 | 0.00000122531 |
| right_thumb_3 | 0.01779 | 0.00000309353 | 0.00000257591 | 0.00000332754 | 3.912100000e-7 | 1.293000000e-8 | -7.61e-9 |
| right_thumb_force_sensor_2 | 0.0001190241979 | 1.022449770e-9 | 9.970397368e-10 | 1.990650573e-9 | -6.741050071e-13 | 1.142558985e-12 | 8.163774587e-12 |
| right_thumb_4 | 0.00766 | 0.00000115326 | 5.7535e-7 | 0.00000115929 | 1.6573e-7 | -4.000000000e-11 | -7e-11 |
| right_thumb_force_sensor_3 | 0.0001698938324 | 3.916962267e-9 | 1.418835363e-9 | 5.295254397e-9 | 2.319551342e-14 | -2.766399951e-13 | 1.729506994e-10 |
| right_thumb_force_sensor_4 | 0.00001669912051 | 2.257734537e-11 | 2.307745095e-11 | 4.316374304e-11 | 2.494469806e-15 | 5.299066785e-15 | -1.743975296e-13 |
| right_thumb_force_sensor_1 | 0.0002343458706 | 6.819184579e-9 | 2.923672322e-9 | 9.688908100e-9 | -1.595517439e-10 | 1.721924502e-11 | 1.800005392e-10 |
| right_index_1 | 0.01869000000 | 0.00000359962 | 0.00000120603 | 0.00000379687 | -4.164600000e-7 | -1.660000000e-9 | -6.3e-10 |
| right_index_2 | 0.01102 | 0.00000232185 | 4.134e-7 | 0.000002423840000 | -5.6428e-7 | 9e-11 | 3.9e-10 |
| right_index_force_sensor_2 | 0.0002557484582 | 4.798786451e-9 | 2.439588935e-9 | 7.125703346e-9 | -8.640764081e-11 | -1.503301152e-12 | -3.051324488e-11 |
| right_index_force_sensor_3 | 0.00006796469849 | 1.319748213e-10 | 2.534301348e-10 | 2.805335179e-10 | 5.650600680e-12 | 7.791171225e-13 | 9.121980631e-12 |
| right_index_force_sensor_1 | 0.0002027792621 | 3.380287985e-9 | 1.964126990e-9 | 5.280797327e-9 | -5.046403389e-11 | -2.157017144e-13 | -5.481953344e-12 |
| right_middle_1 | 0.01866 | 0.00000359341 | 0.00000120028 | 0.000003785240000 | -4.005900000e-7 | -1.64e-9 | -1.21e-9 |
| right_middle_2 | 0.01767 | 0.00000463728 | 9.821e-7 | 0.00000500365 | -0.00000135163 | 2.92e-9 | 1.151e-8 |
| right_middle_force_sensor_2 | 0.0002625933144 | 5.042260627e-9 | 2.568078506e-9 | 7.495634362e-9 | 3.966274585e-13 | -3.260414787e-14 | 3.537362087e-12 |
| right_middle_force_sensor_3 | 0.00006649145755 | 1.272277646e-10 | 2.436911645e-10 | 2.758751706e-10 | 1.004765907e-14 | 8.578806283e-15 | 7.612729961e-12 |
| right_middle_force_sensor_1 | 0.0002027793883 | 3.382084105e-9 | 1.962332046e-9 | 5.280798400e-9 | 1.875695744e-13 | -1.996472214e-14 | -5.485805623e-12 |
| right_ring_1 | 0.01869000000 | 0.00000360961 | 0.00000120307 | 0.00000378952 | -3.8725e-7 | -2.195000000e-8 | -1.3659e-7 |
| right_ring_2 | 0.01102 | 0.000002347110000 | 3.9493e-7 | 0.00000241823 | -5.196000000e-7 | -2.702e-8 | -1.066800000e-7 |
| right_ring_force_sensor_2 | 0.0002557484556 | 4.794460014e-9 | 2.443915055e-9 | 7.125702906e-9 | 1.328675872e-10 | 1.331996950e-12 | -3.052124340e-11 |
| right_ring_force_sensor_3 | 0.00006796503922 | 1.322683816e-10 | 2.531397442e-10 | 2.805362436e-10 | -8.210054530e-12 | -2.638624266e-13 | 9.151062356e-12 |
| right_ring_force_sensor_1 | 0.0002027792234 | 3.377995402e-9 | 1.966419578e-9 | 5.280797358e-9 | 7.607960917e-11 | 2.738543978e-13 | -5.479474312e-12 |
| right_little_1 | 0.01869000000 | 0.000003634640000 | 0.00000119929 | 0.00000376746 | -3.0236e-7 | -3.342000000e-8 | -2.7369e-7 |
| right_little_2 | 0.01166 | 0.00000229937 | 4.633500000e-7 | 0.00000233336 | -4.8052e-7 | -5.047e-8 | -1.984e-7 |
| right_little_force_sensor_2 | 0.0002802653638 | 5.361055654e-9 | 2.789246339e-9 | 8.010552968e-9 | 2.908710239e-10 | -4.237044402e-12 | 3.607345460e-11 |
| right_little_force_sensor_3 | 0.00006105399217 | 1.115923560e-10 | 2.172091128e-10 | 2.520555352e-10 | -1.489254798e-11 | -1.183874819e-12 | 8.078801359e-12 |
| right_little_force_sensor_1 | 0.0002027792902 | 3.365819956e-9 | 1.978595282e-9 | 5.280797556e-9 | 1.510809714e-10 | 5.666571005e-13 | -5.456729485e-12 |

### RH56F1 L

robot name: `RH56F1_L`.

출처: `outputs/data/URDF.zip!URDF/RH56F1/RH56F1_L/urdf/RH56F1_L.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base_link | 0.07939453394 | 0.00002733029617 | 0.00002621652019 | 0.00003568244156 | -1.140201924e-12 | 2.863177765e-8 | -9.868035965e-13 |
| left_thumb_1 | 0.01680000000 | 7.3387e-7 | 2.7925e-7 | 5.8189e-7 | 1.436e-8 | -1.11e-9 | 3.296e-8 |
| left_thumb_2 | 0.06526 | 0.00001378224 | 0.00001184013000 | 0.00002249189 | -0.00000595663 | -1.980000000e-9 | -7.070000000e-9 |
| left_thumb_3 | 0.01333 | 0.00000141987 | 0.00000118482 | 0.000001692100000 | -1.4979e-7 | -6.3e-10 | -1.76e-9 |
| left_thumb_4 | 0.01144000000 | 9.4221e-7 | 3.9966e-7 | 9.478100000e-7 | -1.6288e-7 | -0.0 | 0.0 |
| thumb_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| thumb_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| left_index_1 | 0.01111 | 0.00000204599 | 5.4029e-7 | 0.0000020895 | 3.703e-8 | 1.77e-9 | -9.149e-8 |
| left_index_2 | 0.0103 | 0.000001566900000 | 2.9717e-7 | 0.000001574630000 | 2.2414e-7 | 1.370000000e-8 | -7.84e-8 |
| index_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| index_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| left_middle_1 | 0.01111 | 0.00000204599 | 5.3491e-7 | 0.00000209487 | 3.707e-8 | -4.9e-10 | 3.6e-9 |
| left_middle_2 | 0.01122 | 0.00000192755 | 3.297300000e-7 | 0.00000195229 | 2.9305e-7 | -1.000000000e-11 | 1.000000000e-11 |
| middle_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| middle_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| left_ring_1 | 0.01111 | 0.00000204599 | 5.395600000e-7 | 0.00000209023 | 3.699e-8 | -2.43e-9 | 8.511e-8 |
| left_ring_2 | 0.0103 | 0.000001566900000 | 2.959e-7 | 0.000001575890000 | 2.2425e-7 | -1.176000000e-8 | 6.729e-8 |
| ring_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ring_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| left_little_1 | 0.01111 | 0.00000204599 | 5.527e-7 | 0.00000207708 | 3.681000000e-8 | -4.360000000e-9 | 1.6568e-7 |
| left_little_2 | 0.00839 | 9.3539e-7 | 2.4681e-7 | 9.379400000e-7 | 1.6843e-7 | -1.767000000e-8 | 7.359e-8 |
| little_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| little_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| plam_1 | 0.41238 | 0.00078835939 | 0.00066648352 | 0.00026678122 | -8.875e-7 | 0.00003202881 | 0.000001468120000 |
| plam_2 | 0.01 | 0.00007426273114 | 0.00004540024537 | 0.00003503037891 | -0.000001510622882 | -0.000001382218669 | 0.000003528453872 |
| plam_3 | 0.01 | 0.00007442901513 | 0.00004065949330 | 0.00004248323896 | 0.000002115503417 | 3.526734432e-7 | -0.000003155666219 |
| plam_force_sensor | 0.004494232135 | 2.773434304e-7 | 0.000001259419263 | 0.000001530553067 | 9.291942027e-12 | -1.139956868e-12 | 5.964250324e-9 |

### RH56F1 R

robot name: `RH56F1_R`.

출처: `outputs/data/URDF.zip!URDF/RH56F1/RH56F1_R/urdf/RH56F1_R.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base_link | 0.07939450036 | 0.00002733028699 | 0.00002621651414 | 0.00003568243255 | 4.733960567e-13 | 2.863280053e-8 | 1.904637433e-12 |
| plam_1 | 0.41238 | 0.00078835939 | 0.00066648352 | 0.00026678122 | 8.875e-7 | 0.00003202881 | -0.000001468120000 |
| plam_2 | 0.01 | 0.00007537758836 | 0.00004627688527 | 0.00003553640708 | 0.000001671982064 | -0.000001351383618 | -0.000003666568590 |
| plam_3 | 0.01 | 0.00007442291904 | 0.00004065748593 | 0.00004247852194 | -0.000002114572852 | 3.534193916e-7 | 0.000003158386330 |
| plam_force_sensor | 0.004494239271 | 2.773433474e-7 | 0.000001259425378 | 0.000001530559085 | -5.595174512e-13 | 2.868255368e-13 | 5.964292552e-9 |
| right_thumb_1 | 0.01680000000 | 7.3387e-7 | 2.7925e-7 | 5.8189e-7 | -1.436e-8 | -1.11e-9 | -3.296e-8 |
| right_thumb_2 | 0.06526 | 0.00001378224 | 0.00001184013000 | 0.00002249189 | 0.00000595663 | -1.980000000e-9 | 7.070000000e-9 |
| right_thumb_3 | 0.01333 | 0.00000141987 | 0.00000118482 | 0.000001692100000 | 1.4979e-7 | -6.3e-10 | 1.76e-9 |
| right_thumb_4 | 0.01144000000 | 9.4221e-7 | 3.9966e-7 | 9.478100000e-7 | 1.6288e-7 | -0.0 | -0.0 |
| thumb_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| thumb_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| right_index_1 | 0.01111 | 0.00000204599 | 5.4029e-7 | 0.0000020895 | -3.703e-8 | 1.77e-9 | 9.149e-8 |
| right_index_2 | 0.0103 | 0.000001566900000 | 2.9717e-7 | 0.000001574630000 | -2.2414e-7 | 1.370000000e-8 | 7.84e-8 |
| index_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| index_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| right_middle_1 | 0.01111 | 0.00000204599 | 5.3491e-7 | 0.00000209487 | -3.707e-8 | -4.9e-10 | -3.6e-9 |
| right_middle_2 | 0.01122 | 0.00000192755 | 3.297300000e-7 | 0.00000195229 | -2.9305e-7 | -1.000000000e-11 | -1.000000000e-11 |
| middle_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| middle_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| right_ring_1 | 0.01111 | 0.00000204599 | 5.395600000e-7 | 0.00000209023 | -3.699e-8 | -2.43e-9 | -8.511e-8 |
| right_ring_2 | 0.0103 | 0.000001566900000 | 2.959e-7 | 0.000001575890000 | -2.2425e-7 | -1.176000000e-8 | -6.729e-8 |
| ring_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ring_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| right_little_1 | 0.01111 | 0.00000204599 | 5.527e-7 | 0.00000207708 | -3.681000000e-8 | -4.360000000e-9 | -1.6568e-7 |
| right_little_2 | 0.00839 | 9.3539e-7 | 2.4681e-7 | 9.379400000e-7 | -1.6843e-7 | -1.767000000e-8 | -7.359e-8 |
| little_force_sensor | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| little_tip | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### RH56H1 L

robot name: `RH56H1_L`.

출처: `outputs/data/URDF.zip!URDF/RH56H1-URDF.zip!RH56H1-URDF/RH56H1_L/urdf/RH56H1_L.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| left_hand_base | 0.02984970410 | 0.000004640007855 | 0.000004471248890 | 0.000007510913143 | -8.712919387e-9 | -1.267088688e-7 | -5.501119338e-10 |
| left_hand_palm | 0.2259755564 | 0.0001546770031 | 0.00008611459190 | 0.00008457177628 | -0.000002784149376 | -0.000002458295442 | 0.000008295027261 |
| left_thumb_1 | 0.004887759577 | 2.814382536e-7 | 4.038520113e-7 | 1.941706227e-7 | -3.533780799e-8 | -2.705161908e-8 | -7.248459487e-9 |
| left_thumb_2 | 0.04587452022 | 0.000006873914980 | 0.000006429972582 | 0.000009510987072 | -0.000003121363696 | 7.702114183e-7 | 8.471063766e-7 |
| left_thumb_3 | 0.01363616663 | 0.000001526096400 | 0.000001132024145 | 0.000001707704693 | -5.471268757e-7 | 5.236477012e-8 | 1.465050413e-7 |
| left_thumb_force_sensor | 0.001055981151 | 1.460773461e-8 | 4.039051955e-8 | 5.140980735e-8 | -7.423743847e-12 | 4.339847667e-9 | 1.352397194e-12 |
| left_thumb_tip | 2.218622838e-7 | 2.229606627e-14 | 1.652475702e-14 | 3.614312576e-14 | 1.696752226e-16 | -9.703108179e-17 | 4.846167301e-17 |
| left_index_1 | 0.006299680764 | 2.609117584e-7 | 6.720928725e-7 | 8.409066985e-7 | -7.593437040e-8 | 2.047026942e-8 | 4.462091051e-10 |
| left_index_2 | 0.01148120993 | 3.830385719e-7 | 0.000001360132629 | 0.000001480770563 | -3.968805475e-7 | 3.846061625e-8 | 1.387648373e-8 |
| left_index_force_sensor | 0.001406457153 | 2.244551414e-8 | 4.890734649e-8 | 6.336588575e-8 | 6.297755186e-12 | 2.490324898e-9 | 1.082867142e-12 |
| left_index_tip | 1.916750079e-7 | 1.744330136e-14 | 1.294880365e-14 | 2.829411136e-14 | 1.504474838e-16 | -7.632516211e-17 | 3.620810193e-17 |
| left_middle_1 | 0.006299685155 | 2.601905451e-7 | 6.720925316e-7 | 8.416282920e-7 | -7.590380732e-8 | 1.911983535e-10 | -2.205483691e-9 |
| left_middle_2 | 0.01204640205 | 4.148239064e-7 | 0.000001505261954 | 0.000001642403802 | -4.445250765e-7 | 4.075100317e-11 | 1.041028164e-11 |
| left_middle_force_sensor | 0.001406455454 | 2.244554674e-8 | 4.890723919e-8 | 6.336581604e-8 | 6.292565517e-12 | 2.490324461e-9 | 1.085499984e-12 |
| left_middle_tip | 1.916775962e-7 | 1.743943844e-14 | 1.294914974e-14 | 2.829054943e-14 | 1.496206257e-16 | -7.621039592e-17 | 3.655592571e-17 |
| left_ring_1 | 0.006299666700 | 2.605777980e-7 | 6.720920146e-7 | 8.412383780e-7 | -7.581940640e-8 | -1.502365478e-8 | -4.192485851e-9 |
| left_ring_2 | 0.01148130488 | 3.824445785e-7 | 0.000001360134029 | 0.000001481367957 | -3.969888401e-7 | -2.871797584e-8 | -1.037959913e-8 |
| left_ring_force_sensor | 0.001406455248 | 2.244560651e-8 | 4.890717759e-8 | 6.336581314e-8 | 6.306798663e-12 | 2.490326507e-9 | 1.087431128e-12 |
| left_ring_tip | 1.916750390e-7 | 1.744285288e-14 | 1.294871211e-14 | 2.829356352e-14 | 1.504374550e-16 | -7.629075551e-17 | 3.628367676e-17 |
| left_pinky_1 | 0.006299675571 | 2.612798978e-7 | 6.720933104e-7 | 8.405389485e-7 | -7.573535843e-8 | -2.514663553e-8 | -5.515208440e-9 |
| left_pinky_2 | 0.009044444614 | 2.720556758e-7 | 8.784511502e-7 | 9.528592210e-7 | -2.475446860e-7 | -2.977943425e-8 | -1.081532745e-8 |
| left_pinky_force_sensor | 0.001406454496 | 2.244561790e-8 | 4.890713495e-8 | 6.336578390e-8 | 6.317173781e-12 | 2.490324375e-9 | 1.081995421e-12 |
| left_pinky_tip | 1.916732782e-7 | 1.744462657e-14 | 1.294843376e-14 | 2.829508340e-14 | 1.507291818e-16 | -7.634239017e-17 | 3.612201212e-17 |
| left_palm_casing | 0.01601980776 | 0.00001935465157 | 0.00001207716174 | 0.000007726721567 | -6.914448169e-8 | -2.574539619e-7 | 3.277897064e-7 |
| left_plam_force_sensor | 0.001803467651 | 7.271221771e-8 | 4.172962690e-7 | 4.895191848e-7 | -2.041907006e-10 | -6.800339116e-12 | -1.496101955e-11 |

### RH56H1 R

robot name: `1111111`.

출처: `outputs/data/URDF.zip!URDF/RH56H1-URDF.zip!RH56H1-URDF/RH56H1_R/urdf/RH56H1_R.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| right_hand_base | 0.02984965117 | 0.000004640002288 | 0.000004471243102 | 0.000007510903009 | 8.712852021e-9 | -1.267087691e-7 | 5.501339222e-10 |
| right_hand_palm | 0.2259703473 | 0.0001546702457 | 0.00008611122736 | 0.00008456851211 | 0.000002783265145 | -0.000002459205408 | -0.000008292587543 |
| right_thumb_1 | 0.004887759577 | 2.814382536e-7 | 4.038520113e-7 | 1.941706227e-7 | 3.533780799e-8 | -2.705161908e-8 | 7.248459487e-9 |
| right_thumb_2 | 0.04587288317 | 0.000006873580796 | 0.000006429956858 | 0.000009510805973 | -0.000003121619279 | -7.703273641e-7 | -8.468474371e-7 |
| right_thumb_3 | 0.01363671154 | 0.000001526273547 | 0.000001132143132 | 0.000001707856460 | -5.472307461e-7 | -5.237157673e-8 | -1.465508120e-7 |
| right_thumb_force_sensor | 0.001056012723 | 1.460788385e-8 | 4.039258595e-8 | 5.141187144e-8 | 6.730865224e-13 | 4.340175841e-9 | -2.810689161e-14 |
| right_thumb_tip | 2.220619608e-7 | 2.225632919e-14 | 1.660401186e-14 | 3.618089195e-14 | -5.155085130e-17 | 9.033609214e-17 | 2.331917632e-18 |
| right_index_1 | 0.006300135061 | 2.602033395e-7 | 6.721470583e-7 | 8.416867458e-7 | 7.591094710e-8 | 2.068373212e-10 | 2.200527866e-9 |
| right_index_2 | 0.01148137229 | 3.830297491e-7 | 0.000001360114186 | 0.000001480731572 | 3.968769925e-7 | 3.846157782e-8 | -1.386899385e-8 |
| right_index_force_sensor | 0.001406334256 | 2.244381849e-8 | 4.889965649e-8 | 6.335667838e-8 | 7.247861364e-12 | 2.490919036e-9 | 1.002131183e-12 |
| right_index_tip | 1.918574337e-7 | 1.740928963e-14 | 1.301370687e-14 | 2.832347732e-14 | -2.359715662e-17 | 7.067589775e-17 | -3.409194942e-19 |
| right_middle_1 | 0.006300166403 | 2.602048335e-7 | 6.721471983e-7 | 8.416883784e-7 | 7.591052710e-8 | 2.068160351e-10 | 2.201195098e-9 |
| right_middle_2 | 0.01204626026 | 4.148065642e-7 | 0.000001505199503 | 0.000001642326692 | 4.444987864e-7 | 1.243582260e-11 | 3.192925947e-13 |
| right_middle_force_sensor | 0.001406334056 | 2.234695367e-8 | 4.889968010e-8 | 6.345345543e-8 | 7.258612481e-12 | 1.494867744e-9 | 1.117072835e-12 |
| right_middle_tip | 1.918551362e-7 | 1.740550667e-14 | 1.301330882e-14 | 2.831930211e-14 | -2.475272037e-17 | 7.068403192e-17 | 2.862705608e-20 |
| right_ring_1 | 0.006300151241 | 2.605915950e-7 | 6.721469588e-7 | 8.412998007e-7 | 7.582674517e-8 | -1.500937133e-8 | 4.188479289e-9 |
| right_ring_2 | 0.01148153146 | 3.824395652e-7 | 0.000001360117159 | 0.000001481333617 | 3.969865316e-7 | -2.871391689e-8 | 1.038578524e-8 |
| right_ring_force_sensor | 0.001406338171 | 2.244381726e-8 | 4.889971794e-8 | 6.335671454e-8 | 7.332321106e-12 | 2.490920552e-9 | 1.024567837e-12 |
| right_ring_tip | 1.918569107e-7 | 1.740824933e-14 | 1.301367569e-14 | 2.832240828e-14 | -2.381805455e-17 | 7.067826288e-17 | -2.656714451e-19 |
| right_pinky_1 | 0.006300153361 | 2.612934330e-7 | 6.721471532e-7 | 8.406000377e-7 | 7.574101351e-8 | -2.513333367e-8 | 5.511632360e-9 |
| right_pinky_2 | 0.009044247927 | 2.720475581e-7 | 8.784312818e-7 | 9.528323164e-7 | 2.475347484e-7 | -2.978526189e-8 | 1.081117398e-8 |
| right_pinky_force_sensor | 0.001406338380 | 2.244380382e-8 | 4.889973748e-8 | 6.335672504e-8 | 7.338202100e-12 | 2.490924414e-9 | 1.014093389e-12 |
| right_pinky_tip | 1.918577176e-7 | 1.740980732e-14 | 1.301384772e-14 | 2.832413783e-14 | -2.337031793e-17 | 7.067466659e-17 | -4.359439970e-19 |
| right_palm_casing | 0.01601339194 | 0.00001934838454 | 0.00001207464963 | 0.000007722774482 | 6.925424980e-8 | -2.573942177e-7 | -3.263163337e-7 |
| right_plam_force_sensor | 0.001803313808 | 7.270719638e-8 | 4.172293365e-7 | 4.894472861e-7 | 2.401090560e-10 | 1.069456184e-11 | -1.467527654e-11 |

### RH5DG2 R

robot name: `RH5DG2_R`.

출처: `outputs/data/URDF.zip!URDF/RH5DG2/RH56DG2_R.zip!RH56DG2_R/urdf/RH56DG2_R.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| right_hand_base | 0.08162727654 | 0.00002751046866 | 0.00002642222433 | 0.00003629354818 | -4.859121638e-11 | 3.171864867e-8 | 1.094599306e-11 |
| right_hand_palm | 0.2611098889 | 0.0003011828146 | 0.0002386955931 | 0.0001018255682 | 0.000003179959111 | -0.00002151022450 | -0.000002010568109 |
| right_thumb_yaw | 0.004817354503 | 1.778834164e-7 | 9.586596717e-8 | 1.659312182e-7 | -1.485234879e-8 | -1.102237463e-9 | 5.543724769e-11 |
| right_thumb_mcp | 0.04175607115 | 0.000004599793417 | 0.000006840882541 | 0.000008654110627 | -0.000001454701069 | 5.588706309e-9 | 6.024280360e-9 |
| right_thumb_pip | 0.04138096334 | 0.000004968504650 | 0.000006854576433 | 0.000008678072286 | -0.000001319072416 | 8.889599939e-9 | 4.373395903e-9 |
| right_thumb_dip | 0.007376361360 | 4.789650754e-7 | 8.075085025e-7 | 8.313531443e-7 | -3.846243806e-8 | -9.998476102e-11 | -7.913940554e-11 |
| right_thumb_force_sensor | 0.0008215441274 | 3.905821293e-8 | 1.765501499e-8 | 4.940264426e-8 | -1.273203863e-11 | 1.983272703e-12 | -9.025114391e-9 |
| right_index_yaw | 0.001534984468 | 4.000762161e-9 | 4.611024049e-8 | 4.795441549e-8 | 6.303382642e-23 | -9.576539896e-24 | 2.467262293e-11 |
| right_index_mcp | 0.01282476912 | 0.000001461394384 | 7.300179044e-7 | 0.000001870597169 | -1.663618608e-7 | 5.730659748e-8 | 7.213305353e-9 |
| right_index_pip | 0.005744746475 | 5.225575558e-7 | 4.523035567e-7 | 5.218596236e-7 | 7.923679634e-8 | -2.231899815e-10 | 2.011371333e-9 |
| right_index_dip | 0.006649773227 | 5.743277749e-7 | 2.126710405e-7 | 5.215930560e-7 | -1.183363499e-7 | 2.267081264e-11 | -2.990844678e-11 |
| right_index_force_sensor | 0.0008215234364 | 3.905776782e-8 | 1.765460780e-8 | 4.940197287e-8 | -1.313111022e-11 | 1.866463373e-12 | -9.025009174e-9 |
| right_middle_yaw | 0.001534984468 | 4.000762161e-9 | 4.611024049e-8 | 4.795441549e-8 | 6.212297092e-23 | -1.182445363e-23 | 2.467262293e-11 |
| right_middle_mcp | 0.01282476885 | 0.000001461394377 | 7.300178782e-7 | 0.000001870597139 | -1.663618507e-7 | 5.730659732e-8 | 7.213307362e-9 |
| right_middle_pip | 0.005744746420 | 5.225575534e-7 | 4.523035472e-7 | 5.218596125e-7 | 7.923680069e-8 | -2.231859274e-10 | 2.011372716e-9 |
| right_middle_dip | 0.007909026292 | 9.651551737e-7 | 2.753185691e-7 | 9.190771642e-7 | -1.383270237e-7 | 6.814704296e-11 | -2.700986092e-11 |
| right_middle_force_sensor | 0.0008215236267 | 3.905775904e-8 | 1.765461730e-8 | 4.940197870e-8 | -1.312898104e-11 | 1.862481529e-12 | -9.025005392e-9 |
| right_ring_mcp | 0.01268412256 | 0.000001414178263 | 7.233008173e-7 | 0.000001826887431 | -1.666844746e-7 | 5.540648927e-8 | 8.864337094e-9 |
| right_ring_pip | 0.005744746577 | 5.225575562e-7 | 4.523035716e-7 | 5.218596426e-7 | 7.923678896e-8 | 2.231943414e-10 | -2.011370754e-9 |
| right_ring_dip | 0.007518951815 | 6.809772309e-7 | 2.426952677e-7 | 6.384839354e-7 | -1.149170009e-7 | 1.998788428e-11 | 1.114564233e-10 |
| right_ring_force_sensor | 0.0008215237684 | 3.905776383e-8 | 1.765462364e-8 | 4.940198844e-8 | -1.313508076e-11 | 1.860057335e-12 | -9.025008118e-9 |
| right_pinky_mcp | 0.01268412274 | 0.000001414178286 | 7.233008250e-7 | 0.000001826887461 | -1.666844725e-7 | 5.540649357e-8 | 8.864348339e-9 |
| right_pinky_pip | 0.005744746474 | 5.225575558e-7 | 4.523035567e-7 | 5.218596236e-7 | 7.923679632e-8 | -2.231899641e-10 | 2.011371331e-9 |
| right_pinky_dip | 0.006398790742 | 7.463788389e-7 | 2.109789569e-7 | 7.030648251e-7 | -1.045355744e-7 | 1.577985777e-11 | -4.532778814e-11 |
| right_pinky_force_sensor | 0.0008215230643 | 3.905776761e-8 | 1.765460168e-8 | 4.940196655e-8 | -1.313451935e-11 | 1.861951839e-12 | -9.025008023e-9 |
| right_palm_force_sensor | 0.005102735173 | 4.178311337e-7 | 0.000001541248701 | 0.000001923332697 | -2.118835435e-8 | 9.215279505e-9 | 9.859097442e-9 |
| right_hand_casing | 0.02163166363 | 0.00005116875931 | 0.00003142125121 | 0.00002351889455 | 9.937257284e-8 | -0.000001938005894 | 1.878823902e-7 |

### RH5DG2 L

robot name: `RH5DG2_L`.

출처: `outputs/data/URDF.zip!URDF/RH5DG2/RH5DG2_L.zip!RH5DG2_L/urdf/RH5DG2_L.urdf`.

| 링크 | Mass (kg) | ixx | iyy | izz | ixy | ixz | iyz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| left_hand_base | 0.08162724319 | 0.00002751046437 | 0.00002642220335 | 0.00003629353162 | 5.123935237e-11 | 3.171820099e-8 | -9.189358406e-12 |
| left_hand_palm | 0.2616711202 | 0.0003041950792 | 0.0002413243808 | 0.0001022222716 | -0.000003146816535 | -0.00002159842988 | 0.000002906990200 |
| left_thumb_yaw | 0.004817398943 | 1.778842715e-7 | 9.586682882e-8 | 1.659311670e-7 | 1.485220807e-8 | -1.102242944e-9 | -5.577629398e-11 |
| left_thumb_mcp | 0.04175584871 | 0.000004599825175 | 0.000006840840110 | 0.000008654102025 | 0.000001454765277 | -5.574554142e-9 | 6.020579757e-9 |
| left_thumb_pip | 0.04138153842 | 0.000004968606648 | 0.000006854703504 | 0.000008678267388 | 0.000001319175928 | -8.871800780e-9 | 4.361266345e-9 |
| left_thumb_dip | 0.007376477044 | 4.789765133e-7 | 8.075055017e-7 | 8.313605465e-7 | 3.845569318e-8 | 1.021102255e-10 | -7.922031475e-11 |
| left_thumb_force_sensor | 0.0008557718313 | 4.070649169e-8 | 1.838951919e-8 | 5.147619598e-8 | 2.201868337e-12 | 4.469286774e-12 | 9.408559738e-9 |
| left_index_yaw | 0.001534984468 | 4.000762161e-9 | 4.610991047e-8 | 4.795474552e-8 | 7.095683147e-23 | 1.022787351e-23 | -1.574227157e-24 |
| left_index_mcp | 0.01282476886 | 0.000001461394395 | 7.300178825e-7 | 0.000001870597161 | -1.663618667e-7 | 5.730659733e-8 | 7.213306736e-9 |
| left_index_pip | 0.005744752521 | 5.225585352e-7 | 4.523039156e-7 | 5.218611313e-7 | 7.923750856e-8 | 2.283086245e-10 | -2.018180621e-9 |
| left_index_dip | 0.006649827639 | 5.743240810e-7 | 2.126715532e-7 | 5.215911801e-7 | -1.183373379e-7 | -1.690249341e-11 | 4.427844928e-11 |
| left_index_force_sensor | 0.0008557598683 | 4.070637267e-8 | 1.838938963e-8 | 5.147605739e-8 | 3.416388107e-12 | -4.202814386e-12 | -9.408315032e-9 |
| left_middle_yaw | 0.001534984468 | 4.000762161e-9 | 4.610991047e-8 | 4.795474552e-8 | 2.211896558e-23 | 1.650483579e-23 | -9.268147310e-24 |
| left_middle_mcp | 0.01282476826 | 0.000001461394243 | 7.300178841e-7 | 0.000001870597014 | -1.663618521e-7 | 5.730659851e-8 | 7.213307501e-9 |
| left_middle_pip | 0.005744752471 | 5.225585333e-7 | 4.523039065e-7 | 5.218611205e-7 | 7.923751312e-8 | 2.283123020e-10 | -2.018179238e-9 |
| left_middle_dip | 0.007909089008 | 9.651613277e-7 | 2.753208779e-7 | 9.190848437e-7 | -1.383282494e-7 | -7.015431821e-11 | 1.736309010e-11 |
| left_middle_force_sensor | 0.0008557597515 | 4.070637146e-8 | 1.838938830e-8 | 5.147605496e-8 | 3.417042521e-12 | -4.202828687e-12 | -9.408314625e-9 |
| left_ring_mcp | 0.01268412184 | 0.000001414178122 | 7.233008041e-7 | 0.000001826887282 | -1.666844626e-7 | 5.540649088e-8 | 8.864345498e-9 |
| left_ring_pip | 0.005744752489 | 5.225585296e-7 | 4.523039147e-7 | 5.218611267e-7 | 7.923750763e-8 | 2.283084222e-10 | -2.018179333e-9 |
| left_ring_dip | 0.007518906854 | 6.809860213e-7 | 2.426971420e-7 | 6.384938333e-7 | -1.149221776e-7 | -1.889695585e-11 | -9.561921838e-11 |
| left_ring_force_sensor | 0.0008557598402 | 4.070637325e-8 | 1.838938933e-8 | 5.147605789e-8 | 3.416167568e-12 | -4.202302140e-12 | -9.408314935e-9 |
| left_pinky_mcp | 0.01268412185 | 0.000001414178098 | 7.233008073e-7 | 0.000001826887258 | -1.666844596e-7 | 5.540649118e-8 | 8.864340182e-9 |
| left_pinky_pip | 0.005744752481 | 5.225585286e-7 | 4.523039143e-7 | 5.218611260e-7 | 7.923750765e-8 | 2.283083964e-10 | -2.018179776e-9 |
| left_pinky_dip | 0.006398736864 | 7.463855103e-7 | 2.109780907e-7 | 7.030716539e-7 | -1.045345901e-7 | -2.006809438e-11 | 5.419038725e-11 |
| left_pinky_force_sensor | 0.0008557589536 | 4.070636645e-8 | 1.838936519e-8 | 5.147602491e-8 | 3.416104921e-12 | -4.201185147e-12 | -9.408311742e-9 |
| left_palm_force_sensor | 0.005102714649 | 4.180135015e-7 | 0.000001542450648 | 0.000001921990140 | 2.520797100e-8 | -1.017075208e-8 | 2.484495163e-8 |
| left_hand_casing | 0.02164116409 | 0.00005118416944 | 0.00003142620750 | 0.00002353268737 | -1.017124402e-7 | -0.000001939978488 | -1.834783131e-7 |

## Xacro 대조

URDF 파일과 함께 제공된 Xacro도 확인했다. include 래퍼는 별도 물리 모델로 집계하지 않았으며, 선언된 include 경로에 있는 URDF가 동일 압축 내부에 존재하는지 대조했다. 매크로 실행·ROS 패키지 로딩은 하지 않았다.

| Xacro 출처 | 대조 결과 |
| --- | --- |
| outputs/data/SDK.zip!SDK/ros2.rar!ros2/四代手控制程序/inspire_hand_Linkage.zip!src/urdf_left_with_force_sensor/urdf/urdf_left_with_force_sensor.xacro | URDF include 래퍼; 물리 설정은 포함 대상 URDF 참조 |
| outputs/data/SDK.zip!SDK/ros2.rar!ros2/四代手控制程序/仿真+硬件联合驱动/inspire_hand_Linkage.zip!src/urdf_left_with_force_sensor/urdf/urdf_left_with_force_sensor.xacro | URDF include 래퍼; 물리 설정은 포함 대상 URDF 참조 |
| outputs/data/SDK.zip!SDK/urdf.rar!src/urdf_left_with_force_sensor/urdf/urdf_left_with_force_sensor.xacro | URDF include 래퍼; 물리 설정은 포함 대상 URDF 참조 |
| outputs/data/URDF.zip!URDF/RH56E2 URDF.zip!RH56E2_L_2025_9_10/urdf/RH56E2_L_2025_9_10.xacro | Effort·Velocity·Mass·Inertia 모두 URDF와 동일 |
| outputs/data/URDF.zip!URDF/RH56E2 URDF.zip!RH56E2_R_2025_9_11/urdf/RH56E2_R_2025_9_11.xacro | Effort·Velocity·Mass·Inertia 모두 URDF와 동일 |
| outputs/data/URDF.zip!URDF/RH56F1/RH56F1_L/urdf/RH56F1_L.xacro | Effort·Velocity·Mass·Inertia 모두 URDF와 동일 |
| outputs/data/URDF.zip!URDF/RH56F1/RH56F1_R/urdf/RH56F1_R.xacro | Effort·Velocity·Mass·Inertia 모두 URDF와 동일 |
| outputs/data/URDF.zip!URDF/RH56H1-URDF.zip!RH56H1-URDF/RH56H1_L/urdf/RH56H1_L.xacro | URDF include 래퍼; 물리 설정은 포함 대상 URDF 참조 |
| outputs/data/URDF.zip!URDF/RH56H1-URDF.zip!RH56H1-URDF/RH56H1_R/urdf/RH56H1_R.xacro | URDF include 래퍼; 물리 설정은 포함 대상 URDF 참조 |
| outputs/data/URDF.zip!URDF/RH5DG2/RH56DG2_R.zip!RH56DG2_R/urdf/RH5DG2_R.xacro | Effort·Velocity·Mass·Inertia 모두 URDF와 동일 |
| outputs/data/URDF.zip!URDF/RH5DG2/RH5DG2_L.zip!RH5DG2_L/urdf/RH5DG2_L.xacro | Effort·Velocity·Mass·Inertia 모두 URDF와 동일 |

## 최종 대조·영향·검증 범위

- SDK의 세 URDF는 SHA-256이 같으며 1종으로 집계했다. 연결된 Xacro 래퍼도 3개가 동일하다.
- RH56E2 L: 회전 12관절 모두 effort=1, velocity=2. R: 엄지 4관절 velocity=2, 나머지 8관절 velocity=1.
- RH56F1 L/R의 질량 0 링크는 각각 센서 5개와 tip 5개, 총 10개다. 해당 링크는 관성 6성분도 모두 0이다.
- RH56H1 R의 robot name은 원문에서 1111111이다. 파일 경로를 기준으로 모델을 식별했다.
- 전후: 기존 원본은 조회만 수행했고 비교 기록·스크립트·JSON만 추가했다. 환경 물리 설정·학습 동작에 영향이 없다.
- 검증: 모든 압축 목록 조회/대상 파일 읽기, 24개 XML 파싱, 고유 11종의 모든 링크 mass/inertia와 모든 가동 관절 limit 존재 확인, 좌우 링크 키 완전 대응, Xacro 6개 직접 선언값 동일 및 include 래퍼 5개 대상 존재 대조를 수행했다.
- 미검증: Xacro 실행, ROS/Isaac/PhysX import와 고정 링크 병합 후 관성·질량, 실제 장비 사양·측정값·학습은 확인하지 않았다.

추가 검증 기록(2026-11-14): 별도 minidom 파서로 24개 XML의 링크·관절 수 및 Mass·Inertia·limit 수치 문자열을 재대조해 모두 일치했다. 상위 원본 압축 3개의 조회 전후 SHA-256이 일치했다. Markdown 수식 검사, 신규 문서 외부 링크 검사(2개), 전체 문서 링크 검사(587개 문서·오류 0), git diff --check가 통과했다.

재현:

```bash
python outputs/urdf_archive_comparison/inspect_archives.py
```
