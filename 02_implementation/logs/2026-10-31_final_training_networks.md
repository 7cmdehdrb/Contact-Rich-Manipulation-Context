# 2026-10-31 Final 학습 네트워크 문서 작성

## 요청과 의도

사용자가 `src/inspire_sweep_baseline` 최신 Final 계열의 Actor·Critic·Actor 관측용 MLP 구조와 loss를 코드에서 확인하여 강화학습 관점의 문서 하나로 정리해 달라고 요청했다. [Final 학습 네트워크 문서](../../04_article/environment_reference/FINAL_TRAINING_NETWORKS.md)를 작성했다. 코드 구현 설명보다 관측 정보, 행동 분포, 가치 추정, GAE와 loss, 학습 신호의 흐름을 중심으로 구성했다.

## 변경 전후와 영향

| 변경 전 | 변경 후 | 영향 |
| --- | --- | --- |
| 환경별 계약에 관측·PPO 정보가 분산 | 하나의 학습 네트워크 설명 문서 추가 | Final v1 계열 및 최신 v0_2_2의 공통 구조와 Final v0의 차원을 구분 |
| 활성 환경 안내에 네트워크 전용 설명 링크 없음 | 안내 링크 추가 | 기존 환경 설명과 중복되는 상세 보상 규칙은 재작성하지 않음 |
| 이번 문서 작성 기록 없음 | 이 개발 로그 추가 | 근거·검증·한계를 후속 에이전트에 인계 |

production 코드, 설정, 상속, 물리 자산, 기존 사용자 변경, submodule HEAD는 변경하지 않았다. `logs/rsl_rl`은 읽거나 수정하지 않았다. GPU 학습 실행은 하지 않았다.

## 근거 범위

2026-10-31 현재 작업트리를 읽었다. 시작 시 root에는 Final v0_2_2 관련 수정·신규 파일 및 IsaacLab submodule 상태 변경이 있었고, 문서 submodule에도 handoff·활성 환경 안내 수정 및 v0_2_2 문서·로그가 있었다. 이 사용자 작업을 유지했다.

- root HEAD: `b0116a7b3d384dd58e4a3f5909a5ecfa9b90d4e6`
- IsaacLab HEAD: `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`
- 문서 submodule HEAD: `50f075a12b06a572980cbd8d4c7bb864279d2f5e`
- 실제 Python: `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`
- 설치된 RSL-RL: `rsl-rl-lib 5.0.1`, PyTorch: `2.7.0+cu128`

프로젝트의 등록 → Final PPO 설정 상속 → FinalV1Model → 관측 결합 모델 → MaskedObstacleEncoder → 설치된 RSL-RL의 모델·분포·PPO 경로를 추적했다. 현재 의존하는 공통 모델·관측·행동 파일만 확인했고 과거 환경 문서를 연쇄적으로 읽지 않았다. 일반 PPO·GAE 배경은 본문에 연결한 원 논문 초록으로 확인했으며 구현별 수식과 수치는 로컬 소스에 근거한다. 글쓰기 참고 검색 결과는 원저자 문체로 확인되지 않아 문체 근거로 채택하지 않았다.

### 주요 소스 SHA256

프로젝트 파일은 `src/inspire_sweep_baseline/inspire_sweep_baseline/agent/` 기준이며 라이브러리 파일은 위 Python 환경의 `Lib/site-packages/rsl_rl/` 기준이다.

| 파일 | SHA256 |
| --- | --- |
| `final_ppo_cfg.py` | `050533E4252CE599DD3F8243B9E264F279AA489350B1971B42CE2F8BA6331843` |
| `final_models.py` | `AE865C5BDB714AF09BCA6A7BEC933B3826B9AB726B96662166B0CB1A8BBA195F` |
| `contact_sweep_clutter_fusion_models.py` | `5EE1F7E5426D4811E17F2459FC7FD77196FE29E6EE47CE6FCD0FEF738A09C658` |
| `contact_sweep_clutter_models.py` | `D71889537D1ABADB6F2A5AF8D673E787CB62666989D0ADD8C130DB6CD2758E32` |
| `algorithms/ppo.py` | `A2D35E7AD7B884C80B7434E7D2CE785A6DA1E18D93C96F1179FBD3A208669F8C` |
| `modules/distribution.py` | `4631EAE1939DCD6B065D79C3C0128A88BA2C6126D08F46944C8795682A208A1B` |

## 수행한 검증

### 실제 모델 CPU probe

PowerShell here-string을 위 Python에 stdin으로 전달하는 일회성 검사로 실제 `FinalV1Model`, `NumericalPPO`, RSL-RL `RolloutStorage`를 import했다. production 테스트 파일은 추가하지 않았다. seed 42, 8개 합성 관측에 `policy=57D`, `privileged=3D`, `obstacles=80D`, action 8D를 사용했다.

확인한 항목:

- Actor latent `(8,73)`, Critic latent `(8,76)`.
- Actor 본체 60,616 + 인코더 3,120 + 표준편차 8 = 63,744개.
- Critic 본체 60,929 + 인코더 3,120 = 64,049개.
- 두 모델의 파라미터 identity가 겹치지 않음.
- entropy 단독 역전파 시 인코더 기울기는 없고 std 파라미터 기울기는 존재함.
- 정책 log probability 손실에서 Actor 인코더 기울기 발생, Critic 기울기는 없음.
- value 회귀 손실에서 Critic 인코더 기울기 발생, Actor 기울기는 없음.
- privileged XYZ를 바꿔도 Actor 출력 동일.
- present=0인 슬롯의 좌표를 NaN으로 바꿔도 Actor 출력 동일.
- 실제 NumericalPPO로 4 step, 1 epoch, 2 mini-batch의 축소 업데이트 수행 후 두 인코더 파라미터 모두 변화. 이는 기본 36 step·8 epoch·4 mini-batch 학습을 실행한 결과가 아님.

probe exit 0. 합성 rollout의 반환 loss는 value `621.444091796875`, surrogate `-0.0035993456840515137`, entropy `11.351505756378174`로 모두 finite였다. 이 수치를 실제 과업 학습 성능으로 해석하지 않는다.

### 기존 Final PPO 테스트

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$taskTestTemp = Join-Path (Get-Location).Path ('outputs/final_network_doc_pytest_' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $taskTestTemp) { throw 'Temporary path already exists' }
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_final_versions.py::test_final_ppo_consumes_57_and_80_dimensions_and_updates -q --basetemp $taskTestTemp
```

결과: **1 passed in 4.05s**, exit 0. 기존 테스트가 검사하는 Final v1·Test-v1·v2·GoalAccuracy v0_1의 실제 모델 생성, 축소 PPO 업데이트, checkpoint strict 복원, 137D 입력 JIT export 일치를 확인했다. 최초 시도는 Windows 기본 pytest 임시 폴더 접근 권한 오류로 setup 단계에서 중단됐다. 새 고유 workspace 임시 경로를 사용한 재실행으로 해결했으며 기존 임시 폴더는 정리하지 않았다.

### 문서 검사

문서 저장소에서 다음 검사를 수행했다.

```powershell
python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/FINAL_TRAINING_NETWORKS.md 02_implementation/logs/2026-10-31_final_training_networks.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
python 00_guidelines/scripts/check_document_links.py
python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/environments/FINAL_TRAINING_NETWORKS.md 02_implementation/logs/2026-10-31_final_training_networks.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
git diff --check
```

결과: 변경 Markdown 3개 수식 검사 통과, 전체 Markdown 418개 및 dataset CSV/XLSX 링크 검사 오류 0, 변경 문서의 workspace 외부 파일 링크 포함 검사 오류 0, diff 공백 검사 통과. 기존 변경 파일에 대한 Git LF→CRLF 안내는 있었으나 공백 오류는 없었다. 본문 최초 링크 검사는 아직 작성 전인 이번 개발 로그 경로만 실패했으며 로그 생성 후 해결했다. 실제 Markdown/Mermaid 렌더링 확인과 구분한다.

## 최종 요청 대조와 미검증 범위

| 요청 | 반영 |
| --- | --- |
| 최신 Final 계열 학습 구조 | 최신 추가 v0_2_2를 포함한 범위·상속 및 공통 구조 명시 |
| Actor 구조와 loss | 정확한 층·활성화·Gaussian 평균/std·PPO 정책 손실·entropy 설명 |
| Critic 구조와 loss | privileged 3D·스칼라 V·clipped value loss·GAE target 설명 |
| Actor 관측용 MLP 구조와 loss | 80→32→16, 별도 auxiliary loss 없음, 정책 기울기로 공동 학습 설명 |
| 강화학습 중심 설명 | 정보 흐름 도식, 관측의 의미, return·advantage·loss, 학습/실행 구분 |
| 코드 확인에 근거한 정확성 | 현재 소스 및 설치 라이브러리 확인, CPU 모델·gradient·업데이트 검사 |

미검증: Isaac Sim 물리 실행, 신규 GPU 학습·수렴·성공률, 실제 checkpoint의 학습된 표현 의미, 다른 머신의 RSL-RL 버전, Markdown/Mermaid의 실제 UI 렌더링. 문서 작업이므로 환경의 실행 전후 동등성 검사는 요구하지 않았으며 코드 변경도 없다.
