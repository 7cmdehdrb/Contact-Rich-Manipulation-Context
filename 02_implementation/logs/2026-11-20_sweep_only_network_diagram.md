# 현재 Sweep Only 신경망 구조도 작성

## 요청과 기준

사용자는 현재 코드 기준의 신경망 구조도를 요청했으며 Actor와 Encoder 포함을 필수로 지정했다. 직전 작업 대상인 `Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach`의 PPO 설정·모델 상속·관측을 확인했다. 구조를 설명하는 그림만 작성했으며 환경·네트워크·학습 설정은 변경하지 않았다.

기준 workspace HEAD는 `dd68f9d3e79ee447dcbdab2183a2b32f6ff7fb46`, 문서 submodule HEAD는 `5074b42a1db5861a4f76d8ebeced425d242e9800`이다. 앞선 작업의 LinearReach 소스·테스트·설명과 v1 보상 문서·그래프 등 미커밋 변경을 그대로 보존했다.

## 확인된 구조

| 요소 | 현재 구조 |
| --- | --- |
| 직접 관측 | 팔 위치6·팔 속도6·손 주 구동 위치6·EEF pose7·타겟 대표점3·목표3·이전 행동12·촉각17·wrench6 = 66D |
| 장애물 관측 | 16개 슬롯의 `[valid,x,y,z]` = 64D |
| Encoder 전처리 | valid가0.5 이하인 슬롯의4개 값을0으로 만든 뒤64D로 펼침 |
| Obstacle Encoder | Linear64→32, ReLU, Linear32→16. 마지막 activation 없음 |
| Actor 결합 입력 | 직접66D + embedding16D = 82D |
| Actor 본체 | Linear82→256, ELU, Linear256→128, ELU, Linear128→64, ELU, Linear64→12 |
| Gaussian 정책 | 평균12D는 Actor 출력, 표준편차12D는 관측과 독립인 학습 파라미터. 초기값 모두1.0, scalar parameterization |
| 학습·추론 | 학습 시 Gaussian 표본, 결정적 추론 시 평균 사용 |
| Critic | Actor와 같은 관측, 별도 Encoder와 본체. 82→256→128→64→1, 은닉 ELU·마지막 Linear |
| 공유·이력 | Actor와 Critic의 파라미터 공유 없음, RNN 없음, 관측 통계 정규화 비활성 |

그림은 Actor의 입력 두 경로·Encoder·결합·본체·분포·12D 출력을 중심으로 그리고 Critic을 아래 별도 경로로 표시했다. 실제 행동 제한은 신경망 외부 Action term에서 적용함을 구분했다. 타겟·장애물 대표점은 reset snapshot이며 현재 EEF 좌표계로만 변환된다는 관측 조건도 명시했다.

## 산출물과 변경 전후

이전에는 현재 모델을 그린 그림이 없었으며 다음 산출물을 추가했다.

- [PNG 구조도](../../../../outputs/sweep_only_network_architecture/sweep_only_network_architecture.png)
- [SVG 구조도](../../../../outputs/sweep_only_network_architecture/sweep_only_network_architecture.svg)
- [확인한 모델 구조·차원 JSON](../../../../outputs/sweep_only_network_architecture/model_summary.json)
- [그림 재생성 스크립트](../../../../outputs/sweep_only_network_architecture/draw_network.py)

정량 차원·최종 activation·Gaussian 파라미터는 설정만으로 추측하지 않고 설치된 RSL-RL의 MLPModel·MLP·GaussianDistribution 코드까지 대조했다. 모델 본체 입력82D와 raw 관측130D를 구분했다.

## 검증

Isaac Sim을 시작하지 않고 실제 `SweepOnlyModel` 클래스를 모듈별로 읽어 CPU에서 Actor·Critic을 생성했다. 현재 runner의 설정값을 동일하게 전달하고 batch2의66D/64D 관측을 입력했다.

- 실제 Linear layer 입출력: Encoder `[[64,32],[32,16]]`, Actor `[[82,256],[256,128],[128,64],[64,12]]`, Critic 마지막 `[64,1]` 확인.
- forward 출력 Actor `[2,12]`, Critic `[2,1]`, latent `[2,82]` 확인.
- Actor·Critic Encoder weight의 메모리 주소가 다름을 확인.
- 학습 표준편차 파라미터 shape `[12]`, 초기값1 확인.
- 파라미터 수 Actor65,800·Critic65,073·Encoder 각각2,608 확인. 그림에는 불필요한 수치를 추가하지 않고 JSON에 보존했다.
- Matplotlib으로 PNG와 SVG를 생성하고 PNG에서 한글·레이블·차원·화살표와 분기 연결을 육안 확인했다. 최초 font에 Unicode 아래첨자 t가 없어 수학 표기로 바꿨으며, Encoder 내부 연결이 배경에 가려지지 않도록 선의 표시 순서를 수정했다.

그림 재생성 명령은 workspace 루트에서 다음과 같다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python outputs/sweep_only_network_architecture/draw_network.py
```

최종 Markdown 수식 검사1파일·외부 상대 링크8개 오류0·workspace와 문서 저장소의 공백 검사를 통과했다. SVG XML도 정상 파싱됐고 JSON의66+16=82와 Actor 출력12D를 재확인했다. 학습·checkpoint 평가·GPU 실행은 이 그림 작업에서 수행하지 않았다. 직전 LinearReach 작업의 GPU 검증 결과를 새로 수행한 결과로 집계하지 않는다. `logs/rsl_rl`과 기존 사용자 소스 변경은 보존했다.

## 코드 근거

- [현재 PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/stabilize_sweep_ppo_cfg.py)
- [SweepOnlyModel](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/stabilize_sweep_models.py)
- [Encoder·입력 결합·export 모델](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/wrench_refactor_models.py)
- [관측 구성](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/stabilize_sweep.py)
