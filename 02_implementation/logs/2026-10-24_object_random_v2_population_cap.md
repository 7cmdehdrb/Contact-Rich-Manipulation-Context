# ObjectRandom-v2 반복 배치 검사와 개수 상한

[로그 안내](README.md) · [현재 환경 계약](../environments/FUSION_HOLDING_V3_FAMILY.md) · [초기 구현·8/8 실패](2026-10-24_fusion_holding_v3.md)

기준일: 2026-10-24, Asia/Seoul. 사용자는7/7 반복 배치가 통과하면 최대7/7, 실패하면6/6으로 설정하도록 요청했다. 실제7/7 검사에서 배치 실패가 발생하여 **ObjectRandom-v2의 커리큘럼 최종값을 Gray6/White6으로 변경했다.**

## 기준과 검사 방법

Workspace main HEAD는 `e3fe8e33f0757254ef7b44fc296c9fcb0d5bdd01`, 문서 main HEAD는 `e8af2cf0089ca1f8d4ed44e13dc2995f4085b349`다. 작업트리에는 직전 Holding-v3 계열 구현·문서와 사용자 녹화 설정 변경이 이미 있었다. 이를 보존하고, 학습 로그·이전 task의 개수 일정은 수정하지 않았다.

실제 Isaac Sim5.1·Windows D3D12·CUDA 환경에서 `Holding-OSC-ObjectRandom-v2`의 reset을 사용했다. `tests/_object_random_population_stress_probe.py`는 다음 조건으로 검사한다.

- 물체 종류·크기를 선택하는 asset seed를0·1·2·3·42로 바꾸며 seed마다 새 simulator 프로세스를 생성한다.
- seed당4환경×20회 reset, 전체 최대400장면을 계획했다. 한 번이라도 배치에 실패하면 해당 개수의 안정성 검사를 중단한다. 계획 수를 실제 통과 수로 집계하지 않는다.
- learning iteration14000에서 Gray 패딩15%·검사 대상 개수를 적용한다. reset seed는 `asset_seed * 10000 + batch`로 바꾼다.
- 기존 원본 구역·간격·밀도·접근 경로·OBB·선반 조건과200회 시도 제한을 그대로 사용한다. 타겟·목표 재추출, 시도 횟수 증가, 겹침 허용을 하지 않는다.
- reset 성공 후 실제 관측 유한성·활성 개수와 simulator에 기록된 위치·yaw·USD에서 얻은 OBB를 다시 검사한다. 실패 시 reset seed·타겟/목표·후보 검사 횟수를 JSON에 남긴다.

## 7/7 결과와 상한 결정

**첫 asset seed0, reset seed0, 첫4환경 배치의 env0에서200회 배치 시도 후 실패했다.** 따라서 다른 seed와 나머지 반복을 성공한 것으로 간주하지 않고 중단했다. 성공한 전체 reset 배치는0개다.

오류는 `No non-overlapping enlarged layout for env 0 after 200 attempts; target/goal unchanged`다. 200회 중 구역·간격 등 원래 generator 조건을 통과해 OBB 검사까지 도달한 후보는39개였으며,39개 모두 OBB/선반 검사에서 탈락했다. 나머지 시도는 generator 내부에서 완전한 후보를 만들지 못했다. 배치 시도에33.297초, 환경 생성 이후 검사에42.125초가 걸렸다. 이것은 유한 탐색의 실패이며7/7 배치가 수학적으로 불가능하다는 증거는 아니다.

실제 실행은 다음 PowerShell loop였다. 정상 Kit 캐시 쓰기를 허용한 환경에서 실행했다. 첫 seed의 실패를 보고 loop가 종료됐다.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
foreach ($assetSeed in @(0,1,2,3,42)) {
  $reportFile="outputs/object_random_population_stress/7x7_seed_$assetSeed.json"
  & C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -u src/inspire_sweep_baseline/tests/_object_random_population_stress_probe.py --headless --population 7 --seed $assetSeed --num_envs 4 --resets 20 --output $reportFile *> "outputs/object_random_population_stress_7x7_seed_$assetSeed.log"
  $trial=Get-Content -Raw $reportFile | ConvertFrom-Json
  Write-Output "seed=$assetSeed status=$($trial.status) layouts=$($trial.passed_layouts)"
  if ($trial.status -ne 'passed') { break }
}
```

근거는 workspace의 `outputs/object_random_population_stress/7x7_seed_0.json`과 `outputs/object_random_population_stress_7x7_seed_0.log`에 저장했다.

## 変更した設定

`ObjectRandomV2CurriculumCfg.obstacle_population.params`에 `final_gray=6, final_white=6`을 명시했다. White3000·Gray4000부터 각각2000간격으로 증가하는 일정을 유지한다. White는11000에서6개, Gray는12000에서6개가 되며 이후6/6으로 고정한다. checkpoint iteration을 되돌리면 해당 단계의 개수로 복원한다.

물리 풀8/8과 관측16슬롯은 유지한다. 활성화하는 개수만 제한하며 미사용 물체는 기존 비활성화 처리를 따른다. ObjectRandom-v1은 기존8/8을 유지한다. Gray 확장률·보상·OSC·성공/실패 조건은 변경하지 않았다.

## 6/6 후속 검증

선택한6/6도 같은 반복 검사를 실행했다. 초기 실행은 reset 자체가 완료된 뒤 독립 검사의 Euler 변환에3차원 tensor를 넘겨 `IndexError`가 발생했다. 이를 배치 실패가 아닌 검사 코드 오류 `probe_error`로 기록하고 성패 판정에서 제외했다. 공식 함수의 입력 계약 `(N,4)`에 맞춰 flatten·reshape를 수정하고 `_retry` 파일명으로 재실행했다.

```powershell
foreach ($assetSeed in @(0,1,2,3,42)) {
  $reportFile="outputs/object_random_population_stress/6x6_seed_${assetSeed}_retry.json"
  & C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -u src/inspire_sweep_baseline/tests/_object_random_population_stress_probe.py --headless --population 6 --seed $assetSeed --num_envs 4 --resets 20 --output $reportFile *> "outputs/object_random_population_stress_6x6_seed_${assetSeed}_retry.log"
  $trial=Get-Content -Raw $reportFile | ConvertFrom-Json
  Write-Output "seed=$assetSeed status=$($trial.status) layouts=$($trial.passed_layouts)"
  if ($trial.status -ne 'passed') { break }
}
```

### 6/6 반복 검사 결과

6/6 재실행은 **5개 asset seed 모두 통과,100회 전체 reset 배치·총400개 장면·배치 실패0건**이다. 모든 활성 물체에 대해 reset 후 실제 위치와 yaw를 사용한 독립 OBB/선반 검사도 통과했다.

| Asset seed | 통과 배치 | 통과 장면 | 환경 생성 이후 검사 시간 |
| --- | --- | --- | --- |
| 0 | 20 | 80 | 17.343초 |
| 1 | 20 | 80 | 17.078초 |
| 2 | 20 | 80 | 22.360초 |
| 3 | 20 | 80 | 21.282초 |
| 42 | 20 | 80 | 25.547초 |

각 `outputs/object_random_population_stress/6x6_seed_<seed>_retry.json`에 배치별 seed·시간·OBB 검사/탈락 수와 마지막 타겟/목표를 남겼다. 집계는 `outputs/object_random_population_stress/summary_6x6.json`이다. 이는 검사한 물체 조합과400장면에서의 통과이며, 모든 가능한 장면이나 장기 학습에서 실패 확률0을 보장하지 않는다. 사용자 지정대로 최종 상한은6/6으로 유지한다.

## CPU 계약 검증 결과

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_holding_v3.py src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py src/inspire_sweep_baseline/tests/test_clutter_layout.py src/inspire_sweep_baseline/tests/test_termination_debug.py
```

**32 passed,5.37초.** 새 상한의11000·12000경계,16000·90000에서도6/6 고정, 되감기와 기존OSC·배치 계약을 확인했다.

## 실제 설정·문서 검증과 한계

상한 변경 후 실제 Isaac Sim registry·EnvCfg·PPO를 다시 로드했다. ObjectRandom-v2의 final_gray/final_white6/6, 직접 상속·관측16슬롯·기존 제어/운동 페널티 계약 검사가 exit0으로 통과했다. 아래 명령의 로그는 `outputs/object_random_population_cap_config_probe.log`다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -u src/inspire_sweep_baseline/tests/_fusion_holding_v3_probe.py --headless
```

변경 Markdown10개의 수식 검사를 통과했고 파일·anchor·workspace 참조 오류0건을 확인했다. 두 저장소의 `git diff --check`도 통과했다. 학습 실행은 수행하지 않았으며,400장면의 reset 통과를 장기 학습 안정성이나 모든 물체 조합의 배치 성공 보장으로 해석하지 않는다.
