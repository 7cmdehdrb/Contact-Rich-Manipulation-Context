# Markdown 문서 형식 규칙

기준일: 2026-09-14. 이 규칙은 저장소에서 Markdown 문서를 새로 작성하거나 수정하는 모든 에이전트에게 적용한다.

## 블록 수식

독립된 블록 수식은 여는 줄과 닫는 줄에 각각 `$$`를 사용한다.

$$
\mathbf{d}=\mathbf{p}_T^W-\left(\mathbf{p}_R^W+\mathbf{R}_R^W\mathbf{p}_C^R\right).
$$

언어 식별자가 `math`인 fenced code block으로 수식을 작성하지 않는다. 블록 수식의 두 `$$` 구분자는 각각 별도 줄에 둔다.

### GitHub 렌더링 안전 규칙 — 2026-09-20 추가

GitHub Markdown에서는 `$$` 사이의 내용도 Markdown 파서와 충돌할 수 있다. 특히 수식 내부에서 `=` 또는 `-`를 **독립된 물리적 줄**로 두면, 바로 위 줄을 Setext heading으로 해석하여 display math가 깨질 수 있다.

다음 형태는 사용하지 않는다.

~~~markdown
$$
\mathbf{s}
=
[
\mathbf{s}_{pp},
\mathbf{s}_{visual}
]
$$
~~~

위 예시에서 `=` 줄은 Markdown의 Setext heading underline으로 오인될 수 있다.

**기본 원칙은 하나의 display equation을 한 개의 Markdown 물리적 줄에 작성하는 것이다.**

~~~markdown
$$
\mathbf{s}=[\mathbf{s}_{pp},\mathbf{s}_{visual},\mathbf{s}_{tactile},s_{step}].
$$
~~~

긴 수식에서 시각적 줄바꿈이 필요하면 Markdown 줄 자체를 쪼개기보다 LaTeX의 정렬 문법을 사용하되, Markdown 구조 문법이 단독 줄의 시작에 나타나지 않게 한다. 가장 안전한 방식은 `aligned` 전체도 한 물리적 줄 안에 두는 것이다.

~~~markdown
$$
\begin{aligned}\mathbf{x}&=f(\mathbf{q})\\\mathbf{y}&=g(\mathbf{x})\end{aligned}
$$
~~~

블록 수식 내부에서 다음 패턴을 독립된 Markdown 줄로 만들지 않는다.

- `=`, `==`, `===` 등 `=`만으로 구성된 줄
- `-`, `---` 등 `-`만으로 구성된 줄
- `# `, `> `, `- `, `* `, `+ `처럼 Markdown heading·blockquote·list로 해석될 수 있는 줄 시작
- 연산자 하나만 떼어 다음 줄로 넘기는 형태

단순한 줄바꿈 자체가 항상 문제인 것은 아니다. 문제의 직접 원인은 **Markdown 구조 문법과 충돌하는 독립 줄**이며, 재발 방지를 위해 이 저장소에서는 한 줄 수식을 기본 스타일로 사용한다.

이 금지 규칙은 수식에만 적용한다. 일반 소스 코드, 명령어, 로그에는 내용에 맞는 fenced code block을 사용할 수 있다.

### GitHub 금지 매크로 및 MathJax 호환성 — 2026-09-21 추가

GitHub 문서가 MathJax를 사용하더라도 **일반 MathJax에서 알려진 모든 매크로가 GitHub Markdown에서 허용되는 것은 아니다.** GitHub의 Markdown 렌더링 계층이 특정 매크로를 차단할 수 있으므로, 로컬 LaTeX·일반 MathJax에서 동작한다는 사실만으로 GitHub 호환성을 가정하지 않는다.

2026-09-21 `docs/literature/reviews/2026-09-21_rl-reward-formulation-comparison.md`에서 `\operatorname{clip}`, `\operatorname{mean}`을 사용한 결과 GitHub가 **`The following macros are not allowed: operatorname`** 오류를 표시하여 해당 수식이 깨지는 문제가 확인되었다. GitHub Markup의 공개 이슈에서도 같은 `\operatorname` 차단 사례가 보고되어 있다: https://github.com/github/markup/issues/1688

이 저장소에서는 다음 규칙을 적용한다.

- **`\operatorname`과 `\operatorname*`을 사용하지 않는다.**
- 표준 내장 연산자는 가능한 경우 `\max`, `\min`, `\cos`, `\exp`처럼 GitHub에서 직접 지원되는 기본 명령을 사용한다.
- 별도 이름이 필요한 연산자는 `\mathrm{clip}`, `\mathrm{mean}`처럼 단순한 `\mathrm{...}` 표기를 우선 사용한다.
- 새로운 LaTeX 매크로를 도입할 때는 일반 LaTeX/MathJax 지원 여부가 아니라 **GitHub Markdown에서 실제 허용되는지** 확인한다. 검증되지 않은 고급·사용자 정의 매크로를 문서에 바로 추가하지 않는다.
- 금지 매크로가 발견되면 수학적 의미를 바꾸지 않는 범위에서 GitHub 안전 표기로 치환하고, 동일 패턴을 검사기에 추가한다.
## 인라인 수식

문장이나 표 안의 짧은 수식은 한 쌍의 `$`로 감싼 표준 인라인 수식으로 작성한다. 수식 안팎에 백틱을 함께 사용하지 않는다.

$l=p_{C,y}^R$

인라인 수식을 코드 인용 형태로 표시하면 렌더러에서 수식과 코드 표기가 겹치거나 수식이 그대로 노출될 수 있다. 따라서 수식에는 `$…$`만 사용하고, 변수명·식 전체를 백틱으로 감싸지 않는다.

## 적용과 확인

- 새 Markdown 문서의 모든 블록 수식에 이 규칙을 적용한다.
- 새 Markdown 문서의 모든 인라인 수식은 `$…$`로 작성하고 백틱을 섞지 않는다.
- 기존 Markdown 문서에 수식을 추가하거나 기존 블록 수식을 수정할 때도 이 규칙을 적용한다.
- 문서 작업 후 언어 식별자가 `math`인 fenced code block이나 백틱을 섞은 인라인 수식이 새로 생기지 않았는지 확인한다.
- 새로 작성하거나 수정한 Markdown 파일은 Push 전에 `python scripts/check_markdown_math.py <changed-file.md> [...]`로 검사한다.
- 검사기는 `$` 블록 안의 독립된 Setext underline(`=`, `-`)·Markdown 구조 문법·닫히지 않은 `$` 블록뿐 아니라, GitHub에서 금지된 수식 매크로, `math` fenced block, 한 블록을 여러 Markdown 물리적 줄로 나눈 display equation도 오류로 처리한다.
- 현재 금지 매크로 목록에는 `\operatorname`이 포함된다. 새 금지 사례가 확인되면 지침과 `scripts/check_markdown_math.py`의 목록을 함께 갱신한다.
- `git diff --check`만으로는 GitHub 렌더링 충돌을 검출할 수 없으므로 위 수식 검사를 별도로 수행한다.
- 요청 범위 밖의 기존 표기까지 자동으로 일괄 수정하지 않는다.

## 변경 기록

### 2026-09-14

- `docs/literature/papers/2024-ozdamar-pushing-in-the-dark.md`의 `math` fenced code block 13개를 `$$` 블록 수식으로 변환했다.
- 수식 내용, 일반 코드 블록, 인라인 수식은 유지했다.
- 변환 후 기존 `math` 수식 코드 블록이 남지 않았고 `git diff --check`를 통과했다.

### 2026-09-14 — 인라인 수식 표기 정비

- `docs/literature/papers/2024-ozdamar-pushing-in-the-dark.md`에서 백틱을 섞은 인라인 수식 100개를 `$…$` 형식으로 변환했다.
- 수식 내용과 주변 문장은 변경하지 않았다.


### 2026-09-20 — GitHub display math 렌더링 충돌 방지

- `$$` 내부에서 `=`를 독립 줄로 둔 수식이 GitHub에서 Setext heading으로 오인되어 렌더링이 깨지는 사례를 확인했다.
- display math는 한 수식을 한 Markdown 물리적 줄에 작성하는 것을 기본 규칙으로 추가했다.
- 긴 수식은 LaTeX `aligned` 등의 내부 문법으로 정리하되 Markdown 구조 문법을 독립 줄로 두지 않도록 했다.
- `scripts/check_markdown_math.py`를 추가하여 변경한 Markdown 파일의 위험 패턴과 닫히지 않은 `$$` 블록을 Push 전에 검사하도록 했다.
- 이번 지침 추가는 재발 방지가 목적이며, 요청에 따라 기존 문서의 잘못 렌더링된 수식은 소급 수정하지 않는다.

### 2026-09-21 — GitHub 금지 MathJax 매크로 검사 추가

- Reward Formulation 비교 문서에서 `\operatorname` 사용 시 GitHub가 `The following macros are not allowed: operatorname`을 표시하여 수식이 렌더링되지 않는 문제를 확인했다.
- 해당 문서의 `\operatorname{clip}`, `\operatorname{mean}`을 각각 `\mathrm{clip}`, `\mathrm{mean}`으로 교체했다.
- 저장소 코드 검색으로 기존 문서에 남아 있던 `\operatorname` 사용처도 확인하여 `\mathrm{...}` 기반 안전 표기로 교체했다. 함께 수정한 문서는 DexTouch, Rotating without Seeing, force-tactile sweeping meeting, binary-tactile-wrench design notes, Haninger compliant contact primitives, UltraDP review dataset 노트다.
- 위 기존 문서에서 이번 수정으로 건드린 display math는 현재 저장소 규칙에 맞게 한 수식을 한 Markdown 물리적 줄로 정규화했다.
- 일반 MathJax 지원과 GitHub Markdown 허용 매크로가 동일하지 않다는 점을 규칙에 명시했다.
- 검사기가 display math의 Markdown 충돌뿐 아니라 금지 매크로와 `math` fenced block, 여러 물리적 줄로 작성한 display equation도 사전에 거부하도록 강화했다.
