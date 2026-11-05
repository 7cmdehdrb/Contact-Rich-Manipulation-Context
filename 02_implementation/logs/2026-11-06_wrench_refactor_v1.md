# Refactor-v1 접촉 조건부 거리 보상

[환경 계약](../environments/WRENCH_REFACTOR_V1_ENVIRONMENT.md) · [부모 계약](../environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md)

## 요청·의도

사용자는 v0를 상속하는 v1,Contact 유지 제거,현재step 접촉시에만거리보상,기존weight의5배를 요청했다. `target_contact` 유지보상 제거로 해석해 작업시작에 알렸으며,거리weight는5→25다. 기존14cm EEF높이제한은 유지하고,접촉 판정은 기존보상의0.01N 타겟–손 합력 기준을 사용한다. 목표내부의무접촉예외는 없다.

기준 workspace HEAD는 `c57087aa629ec0d7205a37f44dc3a595ea7974ec`이며 이전개발·사용자변경이 있는작업트리를 보존했다. 커밋·학습·기존로그삭제는 하지 않았다.

## 구현·전체 대조

같은계열의기존역할별파일에v1 EnvCfg/RewardsCfg/PPOCfg와stateless 거리함수를추가했다. runtime은v0를사용한다. 기존클래스/함수정의를작업전AST와비교하여전부동일함을확인했다.

실제v1설정전체를v0와대조하는검사를probe에추가했다. 허용차이는 `rewards.target_contact=None`, `rewards.target_goal_distance`의함수·threshold_n추가·weight25뿐이다. PPO는experiment_name외에는동일함을검사한다. scene/actions/observations/events/commands/terminations/curriculum/runtime과나머지11보상은보존한다.

테스트는실제거리·접촉함수를사용하여.01N 직전/정확히/직후,EEF1.19m 경계,stale·비유한값,목표안무접촉0,최초접촉즉시지급·접촉상실즉시0을확인한다. 자식설정변경이부모설정을변경하지않는지도검사한다. 기존“모든Refactor CFG는독립”이라는AST검사는v0의독립성검사를유지하며명시적으로v1의세직계상속을허용하도록수정했다.

## 검증

- 실제32환경GUI 초기화·8개커리큘럼경계reset·부분reset·각reset후36step rollout 통과. 질량/마찰/geometry불변,선반30kg·손.790kg,finite관측/보상 확인.
- `outputs/wrench_refactor_validation/v1_gpu/probe_32.json`: elapsed39.75초,reset.067~.099초. 이시간은32환경값이며2048환경에대한성능보장은아니다.
- CPU회귀170개통과(23.05초). 실제Isaac Lab전체설정대조 `V1_CONFIG_DIFF_OK` 통과, PPO는experiment_name외차이없음.
- 새v1의RL학습·32환경직선밀기전과정은실행하지않았다. GUI smoke는기본동작및유한값검사이며학습성능을증명하지않는다.

재현: `tests/_wrench_refactor_probe.py --task Inspire-Wrench-Refactor-v1 --num_envs 32 --device cuda:0 --output outputs/wrench_refactor_validation/v1_gpu`. 설정대조는같은probe에 `--config-only --num_envs 2048 --device cpu`를사용했다.
