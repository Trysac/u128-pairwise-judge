# Testing

## Coverage

- The library maintains branch coverage > 80%.
- Tests are deterministic, avoiding network dependencies.

## Test Suite

- `tests/test_pairwise_judge.py`: Validates the acceptance criteria, including:
    - `test_acceptance_item_1_recorded_llm_swapped_verdicts`: Verifies debiasing logic.
    - `test_acceptance_item_2_verdicts_mapping`: Tests interpretation of various verdict combinations.
    - `test_acceptance_item_3_parse_verdict`: Exercises strict regex parsing.
    - `test_acceptance_item_4_message_escaping`: Ensures XML tags are safely escaped.
    - `test_acceptance_item_5_summarizer`: Tests the math behind win-rate and consistency calculations.
    - `test_acceptance_item_6_limits_and_exceptions`: Verifies input length constraints and error propagation.
    - `test_acceptance_item_7_on_event_sentinel`: Confirms telemetry capturing and exclusion of input text.