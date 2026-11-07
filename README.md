# pairwise-judge

Pairwise LLM-as-judge comparing two responses in both orders to cancel position bias, with strict verdict parsing and win-rate summaries.

## Why pairwise-judge?

Pairwise LLM judges suffer from position bias: they systematically prefer whichever answer is presented first. In addition, loose regex verdict parsers can misinterpret negative statements as votes. `pairwise-judge` performs two-pass evaluation with swapped order and strict verdict parsing to ensure reliable results.

## Installation

```bash
pip install trysac-pairwise-judge
```

## Usage

```python
from pairwise_judge import RecordedLLM, compare, summarize

# Provide replies for both pass 1 (A,B) and pass 2 (B,A)
llm = RecordedLLM(["Reasoning...\nVERDICT: A", "VERDICT: B"])
result = compare(llm, "What is 2+2?", "4", "5")

print(f"Winner: {result.winner}")
summary = summarize([result])
print(f"Win rate A: {summary.win_rate_a}, Consistency: {summary.consistency_rate}")
```

## Public API

- `compare(llm, question, a, b, *, max_tokens=512, max_chars=50_000, on_event=None) -> Comparison`: Performs two-pass evaluation to mitigate position bias.
- `summarize(comparisons) -> Summary`: Aggregates results, treating ties and inconsistencies as 0.5 weights.
- `build_messages(question, first, second, *, criteria=...) -> list[Message]`: Generates structured prompts with XML delimiters.
- `parse_verdict(reply) -> Literal['A', 'B', 'TIE'] | None`: Validates strict verdict format.
- `RecordedLLM(replies)`: Mock for deterministic testing.
- `FakeLLM(fn)`: Mock utilizing a custom callback.
- `JudgeError`: Raised for inputs exceeding `max_chars`.

## Why not pointwise judges?

Pointwise rubric judges require complex, hard-to-calibrate scoring guidelines. Swapped-order pairwise comparison is the industry standard for eliminating positional bias (Zheng et al., MT-Bench).

See [Security](docs/SECURITY.md) for threat model and limits.