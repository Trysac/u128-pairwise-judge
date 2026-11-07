# Project record

## Objective

Provide a robust pairwise LLM-as-judge utility that cancels position bias through two-pass comparisons and ensures reliability via strict verdict parsing.

## Scope

- In scope: Two-pass pairwise comparison, result debiasing, input escaping for XML tags, win-rate aggregation, and deterministic mocks (RecordedLLM, FakeLLM).

## Out of scope

- Pointwise scoring rubrics.
- Elo or Bradley-Terry ranking algorithms.
- Automatic re-asking on invalid judge output.
- Asynchronous execution.

## Factory run u128 (measured from API usage)

| Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|
| generation | gemini-3.8-flash | yes | 4250 | 7991 | 0 | 0 | 0.0166 |
| fix-1 | gemini-3.8-flash | no | 54126 | 1465 | 0 | 174400 | 0.0592 |
| fix-2 | gemini-3.8-flash | no | 9975 | 158 | 0 | 5733 | 0.0085 |
| audit | gemini-3.1-flash-lite | no | 106724 | 683 | 0 | 550955 | 0.0415 |
| docs | gemini-3.1-flash-lite | no | 208682 | 1294 | 0 | 0 | 0.0541 |

Total: $0.1798. Prices: Anthropic list prices.
