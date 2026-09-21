# Markdown 문서 형식 규칙

기준일: 2026-09-21. 이 규칙은 저장소에서 Markdown 문서를 새로 작성하거나 수정하는 모든 에이전트에게 적용한다.

## 1. 기본 원칙

GitHub는 Markdown에서 `$$` display math와 fenced `math` block을 모두 지원한다. 다만 Markdown 문법과 겹치는 문자·escape가 포함된 수식은 fenced `math` block이 더 안전하므로, 이 저장소에서는 **display math의 기본 형식으로 fenced `math` block을 사용한다.**

~~~markdown
```math
\mathbf{d}=\mathbf{p}_T^W-\left(\mathbf{p}_R^W+\mathbf{R}_R^W\mathbf{p}_C^R\right).
```
~~~

`$$`는 짧고 단순하며 Markdown 선처리와 충돌할 escape가 없는 한 줄 식에만 허용한다. `cases`, `aligned`, literal brace, 행 구분 `\\`, escaped punctuation이 필요한 식은 fenced `math` block으로 작성한다.

GitHub 공식 문서: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions

## 2. Display math 작성 규칙

- 새로 작성하거나 수정하는 복잡한 display 수식은 fenced `math` block을 사용한다.
- fenced `math` 내부에는 `$$`를 다시 넣지 않는다.
- `$$` block을 사용할 경우 수식 본문은 한 Markdown 물리적 줄로 작성한다.
- `$$` 내부에서 `=`, `-`, `#`, `>`, list marker 등 Markdown 구조 문법을 독립된 줄로 두지 않는다.
- `\begin{cases}`, `\begin{aligned}`와 같이 `\\` 행 구분이 필요한 수식은 fenced `math` block을 사용한다.
- LaTeX 명령 앞에는 백슬래시 하나를 쓴다. `\\mathrm`, `\\mathbf`, `\\,`, `\\{`처럼 명령 자체가 이중 백슬래시로 저장되지 않게 한다. `\\`는 의도적인 TeX 행 구분에만 사용한다.

## 3. Inline math 작성 규칙

짧은 수식은 `$...$`를 사용한다.

$l=p_{C,y}^R$

Inline math에서는 Markdown과 충돌하기 쉬운 escaped punctuation을 피한다. literal brace가 필요하면 가능한 경우 `\lbrace`, `\rbrace` 같은 이름 있는 delimiter를 사용하고, 복잡해지면 display math로 전환한다.

수식을 일반 inline-code 백틱과 `$`로 동시에 감싸지 않는다. GitHub가 공식 지원하는 특수 inline-math backtick syntax를 의도적으로 사용하는 경우에는 별도로 검증한다.

## 4. GitHub MathJax 호환성

일반 LaTeX 또는 일반 MathJax에서 동작한다고 해서 GitHub에서 허용된다는 보장은 없다.

### 4.1. `\operatorname` 금지

2026-09-21 Reward Formulation 비교 문서에서 `\operatorname{clip}`, `\operatorname{mean}`이 GitHub에서 다음 오류를 발생시켰다.

> The following macros are not allowed: operatorname

따라서 이 저장소에서는 `\operatorname`과 `\operatorname*`을 사용하지 않는다.

- 표준 연산자는 `\max`, `\min`, `\cos`, `\exp` 등 기본 명령을 사용한다.
- 별도 이름이 필요한 경우 `\mathrm{clip}`, `\mathrm{mean}`처럼 단순한 표기를 사용한다.
- 새로운 고급 매크로를 도입하면 GitHub Markdown에서 실제 허용되는지 확인한다.

관련 GitHub Markup 이슈: https://github.com/github/markup/issues/1688

### 4.2. 서식 매크로는 중괄호 인수를 명시

다음처럼 인수를 받는 매크로는 항상 중괄호를 쓴다.

- `\mathbf{1}`
- `\mathbf{x}`
- `\boldsymbol{\tau}`
- `\mathrm{rad}`
- `\text{success}`

`\mathbf1`, `\mathbf x`, `\boldsymbol\tau`처럼 축약하지 않는다.

### 4.3. `\left` / `\right`와 literal brace

`\left`와 `\right`는 반드시 올바른 delimiter와 짝을 이뤄야 한다.

잘못된 예:

~~~latex
\left{ x > 0 \right}
~~~

literal brace를 scalable delimiter로 써야 한다면 LaTeX 자체로는 `\left\{ ... \right\}`가 맞다. 그러나 indicator 조건에서는 이 형태를 피하고 다음처럼 조건을 subscript에 넣는다.

~~~latex
\mathbf{1}_{\{x>0\}}
~~~

2026-09-21 MAT reward에서 `\left\{...\right\}`와 indicator brace가 Markdown/MathJax 경계에서 깨지며 `Missing or unrecognized delimiter for \left` 오류가 발생했기 때문에 이 규칙을 추가했다.

### 4.4. HTML entity 금지

수식 원문에 `&gt;`, `&lt;`, `&amp;` 같은 HTML entity를 직접 넣지 않는다. 수식 source에는 실제 `>`, `<`와 LaTeX 문법을 사용한다.

### 4.5. 우발적 이중 백슬래시 금지

다음은 잘못된 저장 형태다.

~~~latex
\\mathrm{N}
\\mathbf{x}
\\,
~~~

명령에는 백슬래시 하나만 사용한다. `\\`는 `cases`·`aligned` 등에서의 의도적인 행 구분에만 사용한다.

## 5. Indicator 표기

조건 indicator는 다음 형식을 기본으로 한다.

~~~latex
\mathbf{1}_{\{\text{condition}\}}
~~~

`\mathbf{1}\{condition\}`처럼 indicator 뒤에 별도의 brace 집합을 붙이지 않는다. 이 표기는 의미도 덜 명확하고 Markdown/MathJax 처리 과정에서 깨지기 쉽다.

## 6. Push 전 검사

새로 작성하거나 수정한 Markdown 파일은 반드시 다음 검사기를 실행한다.

```bash
python scripts/check_markdown_math.py <changed-file.md> [more.md ...]
```

검사기는 다음을 확인한다.

- GitHub 금지 매크로 (`\operatorname`)
- `\mathbf`, `\mathrm`, `\text`, `\boldsymbol`의 비중괄호 인수
- HTML entity의 수식 내부 유입
- 우발적인 이중 백슬래시
- grouping brace 균형
- `\left` / `\right` 짝과 delimiter 유효성
- `\begin{...}` / `\end{...}` 짝
- fragile indicator 표기
- `$$` block의 Markdown 구조 충돌과 GFM-sensitive escape
- 닫히지 않은 fenced block / `$$` block

`git diff --check`는 별도로 수행한다. `git diff --check`만으로 MathJax 렌더링 문제를 검출했다고 간주하지 않는다.

가능하면 push 후 GitHub 웹 렌더링에서 다음 오류 문자열이 보이지 않는지도 확인한다.

- `The following macros are not allowed`
- `Missing or unrecognized delimiter`
- `Undefined control sequence`

## 7. 변경 기록

### 2026-09-14

- 수식용 일반 code fence와 백틱이 섞인 inline 수식을 정리하는 규칙을 도입했다.

### 2026-09-20

- `$$` 내부의 독립된 `=` 줄이 GitHub Markdown에서 Setext heading으로 오인되는 사례를 확인했다.
- display equation을 한 Markdown 물리적 줄로 유지하고 사전 검사기를 사용하도록 규칙을 추가했다.

### 2026-09-21 — `\operatorname` 오류

- Reward Formulation 비교 문서에서 `\operatorname`이 GitHub의 허용 매크로 정책에 의해 차단되는 문제를 확인했다.
- `\operatorname{clip}`, `\operatorname{mean}`을 GitHub-safe 표기로 교체하고 검사기에 금지 매크로 검사를 추가했다.

### 2026-09-21 — MAT delimiter 및 후속 수식 오류

- MAT 절에서 indicator/reopen reward가 `Missing or unrecognized delimiter for \left` 오류를 발생시키는 것을 확인했다.
- MAT indicator 조건을 `\mathbf{1}_{\{...\}}` 형태로 수정하여 `\left\{...\right\}` 의존성을 제거했다.
- Reward Formulation 비교 문서의 복잡한 display 수식을 GitHub 공식 지원 형식인 fenced `math` block으로 통일했다.
- 문자 단위 재검사에서 `\\mathrm`, `\\mathbf`, `\\,`처럼 우발적으로 이중 저장된 백슬래시도 발견하여 교정 대상으로 추가했다.
- 검사기를 단일 구현으로 재작성하여 금지 매크로뿐 아니라 brace·delimiter·환경 짝, HTML entity, 이중 백슬래시, GFM-sensitive escape까지 검사하도록 했다.
- 기존 지침 파일에 중복 삽입되어 서로 모순되던 display-math 규칙을 제거하고 이 문서를 canonical 규칙으로 재정리했다.
