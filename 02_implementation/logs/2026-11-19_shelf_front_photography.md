# 선반·물체8개 수평 정면 촬영

## 요청·기준·범위

사용자는 현재 환경에서 로봇을 제외하고 환경 랜덤화를 적용한 물체8개를 완전 정면에서
촬영한 서로 다른 이미지20장 이상을 요청했다. Extension 제작·UI 테스트는 필요 없으며
이미지가 주 산출물이다. 이전 로봇 촬영 작업은 중단된 상태를 보존한다.

Workspace HEAD는 `37aea6365192e919176fe46245be73a4fe7126df`, 문서 HEAD는
`1de3604e4a10709635e722f80e94de45c112f044`다. 시작 시 IsaacLab의 기존 변경과
이전 로봇 촬영 스크립트·README·문서3개 변경이 있었다. 해당 변경은 보존했다.

기준은 현재 `StabilizeSweepSceneCfg`가 사용하는 선반과 Revision8종 자산이다.
기존 학습 환경을 수정하지 않고 SceneCfg와 standalone 실행기를 추가했다.

- [촬영 SceneCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/shelf_photography.py)
- [이미지 생성 실행기](../../../../src/inspire_sweep_baseline/scripts/photograph_shelf_front.py)
- [실행 안내](../../../../src/inspire_sweep_baseline/README.md#선반물체-8개-정면-이미지)

## 변경 전후와 최종 대조

| 항목 | 기존 학습 환경 | 촬영 장면 |
| --- | --- | --- |
| 선반 | `WrenchRefactorShelfSpawnerCfg`, 원본 USD, 위치−0.7/0/0m | 동일 자산·spawner·위치 |
| 물체 | `RevisionObjectSpawnerCfg`,8종 | 동일 spawner·텍스처·형상으로8종 각1개 |
| 크기 | source uniform0.9–1.1배 | 같은 범위, 이미지별 재추출 |
| 배치 | target·obstacle·robot·IK에 의존한 학습 reset | 독립 yaw·깊이·좌우 순서·간격, 정면 가림 방지 조건 |
| 카메라 | 학습 task/뷰어별 설정 | 직교, 월드+X에서−X, 동일 eye/target Y·Z |
| 로봇·Manager·PPO | task 계약 | 생성하지 않음; Gym ID 추가 없음 |
| 물리 | task step/reset |0step, 정적 렌더만; 촬영 USD의 rigid body 비활성화 |
| 배경·조명 | 학습 장면 | 선반 뒤 회색 비충돌 배경, 고정 조명 |

요청의8개 스폰을8종 각1개로 해석했다. 원통·직육면체·머그컵·병·크래커 상자·설탕 상자·
수프 캔·커피 캔이다. 현재 source의 YCB fitting fraction0.9와 원본 텍스처를 보존하며
이전 gallery의 fraction1.0이나 별도 색상 설정을 가져오지 않았다.

source 형상·scale 범위를 가져오되, 로봇 없는 정면 사진에서8개가 모두 드러나도록
좌우 투영이8mm 이상 떨어지는 배치에 조건화한다. 학습 환경의 reset 분포와 동일하다는
의미가 아니다. 물체 위치는 실제 회전 bounds로 보정하고 바닥을 상판1.05m에 맞춘다.
회전은−π부터π, 선반 깊이 위치와 좌우 순서·남는 간격도 랜덤화한다. 선반 기둥의 정면
가림을 피하려고 좌우 가장자리에서65mm 여유를 둔다.

카메라는 eye `(1.4,0,1.22)`m, target `(−0.7,0,1.22)`m, 직교 가로폭1.16m다.
사진1920×800, pitch·좌우 사선·roll0도다. 평행 광선이 수평이므로 상판이나 물체
윗면을 내려다보는 원근이 생기지 않는다. 물체 자체의 yaw는 무작위이므로 상자 측면은
나타날 수 있다.

기존 Gym 등록·EnvCfg·runtime·reset/IK·Action·Observation·Reward·Termination·
Curriculum·PPO·로봇 자산은 이번 작업에서 수정하지 않았다. 학습 로그는 건드리지 않았다.

## 실행·실제 검증·산출물

RTX4070·Isaac Sim5.1·`env_isaaclab` Python으로 workspace 루트에서 실행했다.

```powershell
conda activate env_isaaclab
python src/inspire_sweep_baseline/scripts/photograph_shelf_front.py --headless --count 24
```

최종24장 생성 프로세스 exit code0. `outputs/shelf_front_24`에 PNG24장,
`contact_sheet.jpg`, `metadata.json`, `front_scene_001.usdc`를 생성했다.
seed20261119–20261142, 모든 이미지1920×800, 각 metadata에8종 각1개를 확인했다.
24개 RGB SHA-256이 전부 다르고 실제 파일 픽셀로 재계산한 값이 metadata와 일치했다.

전체24장 contact sheet와 개별 원본 이미지를 시각적으로 확인했다. 모든 장면에8개가
보이고 로봇이 없으며 수평 정면 구도다. 추가 색상 열 검사에서는 이미지마다8–9개
색상 구간이 검출됐다. 머그 손잡이/텍스처 때문에 한 물체가 둘로 분리될 수 있어,
이 수치를 물체 개수의 정답 판정으로 사용하지 않았다. 검사값은 `validation.json`에
보존한다. Extension·GUI 조작·학습은 실행하지 않았다.

초기 실행에서 spawner의 잘못된 `__wrapped__` 접근을 확인하고 직접 호출로 수정했다.
다음 초기 결과는 root prim 삭제·재생성 이후 Hydra가 물체를 표시하지 않는 문제가
있어 최종 산출물로 채택하지 않았다. 같은8개 형상을 유지한 채 pose·scale만 갱신하도록
수정한 뒤24장을 다시 생성했고, 이전 실패 PNG와 metadata는 최종 정상 결과로 교체했다.
Python 예외가 Kit 종료 전에 render log에 남도록 오류 출력도 추가했다.

최종 파일 검사는 새 Python2개 `py_compile`, 상위·문서 저장소 `git diff --check`,
변경 Markdown4개의 수식 검사 통과다. 문서 저장소 변경3개 파일의 링크 검사0오류
(내부318·외부4). README 전체 링크 검사에는 기존 GoalAccuracy-v0_2 문서 누락1건이
남아 있으며 이번 새 촬영 링크는 정상이다.

최종 `outputs/shelf_front_24.zip`에는 PNG24장·미리보기·metadata·validation·첫 장면
USD의28개 파일을 넣었다. 크기24,523,224bytes, ZIP CRC 검사 `testzip()` 통과.

학습 분포 일치·실물 정확도·동적 물리 안정성은 검증 대상이 아니다. 정적 USD는 원본
텍스처 자산 경로를 포함할 수 있어 다른 장비에서 열 때 해당 자산 접근성이 필요하다.

## 후속: 부분 가림 사진24장 추가

사용자가 기존 사진에 가림이 없음을 지적하고 부분 가림 케이스를 추가 요청했다.
기존24장은 가림 방지 조건을 사용했으므로 해당 파일을 유지하고 `--occlusion` 모드를
추가했다. 촬영 실행기만 수정하고 SceneCfg·자산·카메라·기존 학습 환경은 유지했다.

```powershell
python src/inspire_sweep_baseline/scripts/photograph_shelf_front.py --headless --occlusion --count 24 --seed 20261219
```

8종 각1개·1920×800·수평 직교 카메라·고정 조명·원본 scale 범위는 이전과 같다.
장면 번호별로2/3/4쌍을 앞뒤로 배치한다. X가 큰 물체가 카메라에 가까우며 앞뒤
물체는 실제3D bounds가 겹치지 않도록 깊이를 분리한다. Y 방향 투영만 중첩시켜
앞 물체가 뒤 물체를 가린다. 다른 그룹끼리는 가로 간격을 둔다.

`instance_id_segmentation_fast`의 실제 이미지별 instance ID와 prim 경로를 연결해
물체 픽셀 수를 센다. 전체 장면을 렌더한 뒤 앞쪽 가림 물체만 잠시 숨긴 비교 렌더를
수행하고 뒤 물체의 `visible_pixels / unobstructed_pixels`를 구한다. 저장 PNG는
앞 물체를 숨기기 전의 정상 RGB다. 비교 후 앞 물체를 복원하므로 첫 장면 USD도8개를
포함한다. `metadata.json`의 `occlusion_checks`에 쌍·픽셀 수·비율을 보존한다.

각 이미지에서3% 초과97% 미만 가시 비율의 실제 부분 가림이 최소1쌍은 있어야 저장한다.
동시에8개 모두100픽셀 이상 보여야 하며 모든 물체 쌍의 XY bounds 비관통을 검사한다.
이 실행의 실제 결과는24장 모두2–4쌍의 부분 가림이었다. 전체24장 contact sheet와
원본3번 이미지를 확인하여 앞뒤 일부 가림·로봇 부재·수평 정면 구도를 확인했다.
렌더 프로세스 exit code0, Python compile 통과. Extension·GUI 테스트·학습은 실행하지 않았다.

출력은 `outputs/shelf_front_occluded_24`이고 이름은 `front_occluded_001.png`부터
`front_occluded_024.png`다. 기존 무가림 기본 경로는 그대로 유지한다. 추가 옵션이
없으면 이전 가림 방지 배치와 RGB 촬영 경로를 사용한다. 신규 메타데이터에는 slot과
world bounds도 기록한다. 카메라 segmentation은 가림 모드에서만 활성화한다.

후속 파일 검증에서24장 모두1920×800·고유 RGB 해시·물체8개·bounds 비관통을 확인했고
실제 부분 가림은 총70쌍이었다. 기존24장도 저장된 RGB 해시와 모두 일치하여 보존을
확인했다. `validation.json`에 결과를 저장하고 PNG24장·미리보기·metadata·validation·
첫 장면 USD를 `outputs/shelf_front_occluded_24.zip`으로 묶었다. ZIP 크기24,365,127bytes,
CRC 검사 통과. 변경 문서3개의 수식·링크 검사0오류(내부320·외부4), 상위·문서 저장소
`git diff --check` 통과. README의 기존 GoalAccuracy-v0_2 누락 링크는 이전과 같다.

## 후속: 거의 보이지 않는 강한 가림24장

사용자가 거의 보이지 않을 정도로 많이 가려진 추가 케이스를 요청했다.
`--heavy-occlusion`을 추가했고 이 옵션은 내부적으로 가림 모드도 활성화한다.
새 출력 폴더는 `outputs/shelf_front_heavy_24`다. 기존 기본 모드·부분 가림 모드의
출력 폴더와 기존48개 PNG는 유지한다. 촬영 실행기만 수정하고 SceneCfg·카메라·
자산·scale 범위·기존 학습 환경은 변경하지 않았다.

```powershell
python src/inspire_sweep_baseline/scripts/photograph_shelf_front.py --headless --heavy-occlusion --count 24 --seed 20261319
```

각 장면의 강한 가림2쌍은 크래커/설탕 상자를 앞에 두고 원통·직육면체·머그 중2개를
뒤에 둔다. 나머지는 기존 랜덤화와2–4쌍 그룹 구성을 따른다. 앞 물체의 회전 투영 폭과
높이가 뒤 물체보다 큰 경우를 선택하고, 뒤 물체의 좁은 가장자리만 노출되도록 맞춘다.
실제3D 관통은 허용하지 않는다.

단순 bounds로 맞추면 스캔 메시의 윤곽 때문에 완전 가림이나10% 초과 노출이 생겼다.
따라서 기존 실제 instance mask 비교값을 피드백으로 사용해 뒤 물체의 Y 위치를
최대12회·최초 위치에서±18mm 이내로 보정한다. 그룹당40mm 여유를 추가해 보정 공간을
확보하고 최종 모든 물체 쌍의 bounds 비관통을 다시 검사한다. 보정 목표 가시 비율은
장면에 따라1.5/2.5/4.5%이며, 실제 저장 허용은0.1% 초과10% 이하의 강한 가림이
최소1개 있는 장면이다.8개 모두 최소20픽셀은 남겨 완전 소실은 피한다.

최종24장 렌더 프로세스 exit code0. 실제로는24장 모두 강한 가림2개씩 총48개가
확인됐으며 가시 비율 범위는0.0055254169–0.0772417154다. 즉0.55–7.72%만 보이고
92.28–99.45%가 가려졌다. 가장 적게 보이는 사례는 `front_heavy_011.png`다.
전체 contact sheet와 원본1·8번 이미지를 확인했고, 수평 정면·로봇 부재·얇게 남는
뒤 물체를 확인했다. 모든 사진은1920×800이며8종 각1개·고유 RGB 해시24개다.

픽셀 해시·물체 개수·실제 강한 가림2개씩·최종 bounds 비관통을 별도 검사하고
`validation.json`에 저장했다. 기존 무가림24장과 부분 가림24장도 각각 metadata의
RGB 해시와 일치하여 미변경을 확인했다. PNG24장·contact sheet·metadata·validation·
첫 장면 USD의28개 파일을 `outputs/shelf_front_heavy_24.zip`으로 묶었다.
크기25,118,733bytes, ZIP CRC 검사 통과. Python compile 및 상위 diff 공백 검사 통과.
Extension·GUI·학습 검증은 실행하지 않았다. 카메라/학습 계약의 변경은 없다.
