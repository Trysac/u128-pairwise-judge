# Security Model

## Threat Model

### Defended

- **Prompt Injection**: The library escapes case-insensitive occurrences of `</question`, `</response_a>`, and `</response_b>` tags by replacing `<` with `&lt;` to prevent structural breakout of the judge prompt.
- **Resource Exhaustion**: The library enforces an input character limit (`max_chars`, default 50,000) on questions and responses. If exceeded, a `JudgeError` with code `input_too_large` is raised before external calls occur.
- **Data Leakage**: The code does not log sensitive data (inputs or completions). Telemetry via `on_event` is restricted to non-sensitive metadata (event, order, verdict, reply character count).

### Not Defended

- **Prompt content safety**: The library does not sanitize the *content* of the prompts beyond the XML tags; it assumes the provided `criteria` and inputs are safe.
- **Judge behavior**: It does not guarantee the judge will follow the 'no instructions' directive if the judge LLM is susceptible to jailbreaking via the provided inputs.