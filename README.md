# pairwise-judge

[![PyPI version](https://img.shields.io/pypi/v/trysac-pairwise-judge)](https://pypi.org/project/trysac-pairwise-judge/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-pairwise-judge)](LICENSE)
[![CI](https://github.com/Trysac/u128-pairwise-judge/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u128-pairwise-judge/actions/workflows/ci.yml)

Pairwise LLM-as-judge comparing two responses in both orders to cancel position bias, with strict verdict parsing and win-rate summaries

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-pairwise-judge
# or
uv add trysac-pairwise-judge
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import pairwise_judge

# normalize() trims surrounding whitespace and lower-cases the text.
print(pairwise_judge.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    pairwise_judge.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
