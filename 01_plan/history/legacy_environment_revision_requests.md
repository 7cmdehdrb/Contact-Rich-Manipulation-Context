# 과거 환경 설정 개정 요청

[문서 안내](../README.md) · [역사 자료 안내](README.md) · [현재 활성 환경](../../02_implementation/08_ACTIVE_ENVIRONMENTS.md)

**상태: HISTORICAL 요청 기록.** 원본은 workspace의 `tests/WTF.md`이며 작성일과 대상 환경은 본문만으로 확정되지 않는다. PPO 설정 별도 추가, Hand 자중을 포함하는 F/T, 참고 환경의 로봇·선반·OSC 파라미터, 선반 좌우 Sweep 방향을 요청한 기록이다. 요청 내용은 보존하되 각 항목이 어느 환경에 구현되었는지 또는 현재 모든 환경에 적용되는지를 증명하는 자료로 사용하지 않는다. 현행 baseline과 변형의 차이는 활성 환경 문서에서 확인한다.

## 당시 요청 원문

다음 사항을 확인 및 반영해라. 이미 반영된 사항이라면 넘기고, 아니라면 개정하라:

1. PPO 설정
example/Sweep-Policy/sweeping_policy/config/ur5e/agents/rsl_rl_ppo_cfg_02.py 를 기본으로 따라가도록 해라.
단, 지금 너가 만든 설정은 유지하고, 새 설정 파일을 만들어서, 저 설정을 사용해라. 다만, max_iter는 10000을 유지한다.

2. F/T 센서
별도의 캔슬레이션이 없는 것으로 취급해라. 즉, Hand 자체의 무게에 의한 힘과 모멘트는 상시 감지되는 구조로 설정된다.

3. 로봇 Configuration 및 shelf 위치.
example/Sweep-Policy/sweeping_policy 기본적으로 여기에 맞춰라.
당연히 가상 EEF Point나 핸드를 포함한 구성 같은건 변경되어야 하지만, 각종 파라미터 등은 여기에 맞춰라

4. OSC
example/Sweep-Policy/sweeping_policy/config/ur5e/osc_random_sweep_env_cfg.py
OSC 파라미터는 기본적으로 여기에 맞춰라. 

5. 환경 구성

밀어야 하는 방향이 잘못 되었다.

       불가능
가능 <- 선반 -> 가능
       불가능

이런 방향의 움직임이여야 한다.

example/Sweep-Policy 를 확인해서 방향을 잡아라.

또한, 선반임을 감안해서 w는 크고 d는 짧은 경향이 있어야 하는데, 지금은 정사각형에 가까워 보인다. 이도 개선해라.

