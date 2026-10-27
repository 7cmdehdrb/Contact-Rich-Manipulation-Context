# Markdown 형식 규칙

[문서 구조](../DOCUMENT_STRUCTURE.md)

- 제목·문단·목록 사이에 빈 줄을 둔다. 코드·명령은 언어를 지정한 fenced block으로 쓴다.
- 다른 문서는 상대 링크로 연결하고 파일과 anchor가 실제로 존재하는지 검사한다.
- 복잡한 수식은 `math` fenced block을 사용한다. inline 수식은 `$...$`를 사용한다.
- 수식 안의 `\operatorname`은 사용하지 않고 `\mathrm{...}` 등 GitHub에서 지원되는 기본 명령을 사용한다. `\mathbf{x}`처럼 인자를 중괄호로 묶는다.
- LaTeX 명령 앞에는 백슬래시 하나만 사용한다. 수식에 HTML entity를 넣지 않는다.
- 변경한 Markdown만 `check_markdown_math.py`에 전달하고 링크 검사와 `git diff --check`를 함께 수행한다. 검사 통과와 실제 렌더링 확인을 구분한다.
