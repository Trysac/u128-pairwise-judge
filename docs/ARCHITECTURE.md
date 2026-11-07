# Architecture

`pairwise-judge` is a standard-library Python utility implementing position-bias mitigation for LLM-as-a-judge pairwise evaluations.

## Position Bias and Debiasing Strategy

LLMs frequently demonstrate strong positional bias when comparing two candidates in a single prompt. To eliminate position bias:

1. The judge is called with candidate `a` in slot `A` and `b` in slot `B` (order `ab`).
2. The judge is called with candidate `b` in slot `A` and `a` in slot `B` (order `ba`).
3. The verdict in the second pass is inverted (`A` becomes `b`, `B` becomes `a`).
4. If both passes agree on `a`, `winner == 'a'`. If both agree on `b`, `winner == 'b'`. If both conclude `TIE`, `winner == 'tie'`. If either reply lacks a valid verdict, `winner == 'invalid'`. If verdicts conflict across the two presentations, `winner == 'inconsistent'`.

## Strict Parsing & Prompt Safety

- Verdict line: The last non-empty line of the LLM response is stripped and matched against `^VERDICT: (A|B|TIE)$` (case-sensitive).
- Delimiter escaping: XML boundaries `<question>`, `<response_a>`, `<response_b>` inside untrusted inputs have any closing variants `</question>`, `</response_a>`, `</response_b>` sanitized so that `<` is replaced with `&lt;`.
- Size limits: Inputs exceeding `max_chars` (default 50,000) immediately raise `JudgeError` with `code='input_too_large'` before making LLM calls.
