# Two-Pass Swapped Order Pairwise Judge with Strict Verdict Parsing

Status: accepted (generated, pending human review)

## Context

Pairwise LLM judges suffer from position bias where candidates presented first receive a systematic advantage. Furthermore, free-form text parsers frequently misidentify negative statements as positive verdicts, and untrusted responses can inject XML delimiter escape tokens.

## Decision

Implement a two-pass swapped order evaluation ('ab' and 'ba') with strict final-line regex validation (^VERDICT: (A|B|TIE)$) and XML delimiter escaping. Calculate both win rate and position consistency rate while excluding invalid responses from denominator calculations.

## Consequences

Position bias is neutralized across candidate comparisons and position bias rate is directly measurable. Tests and consumers can run offline deterministically using RecordedLLM and FakeLLM without network or API dependencies.
