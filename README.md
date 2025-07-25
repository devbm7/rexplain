# rexplain

[![PyPI version](https://img.shields.io/pypi/v/rexplain.svg)](https://pypi.org/project/rexplain/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rexplain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Explain, test, and generate examples for regular expressions.

## Overview

**rexplain** is a Python toolkit for understanding, testing, and generating examples for regular expressions. It provides:
- Human-readable, line-by-line explanations of regex patterns
- Example string generation for any regex
- Detailed match testing with feedback
- Both a Python API and a CLI

## Features
- **Regex Explanation:** Get clear, context-aware explanations for any regex pattern
- **Test Regex:** Test if a string matches a pattern and see why/why not
- **Generate Examples:** Generate example strings that match a regex
- **CLI & API:** Use from the command line or as a Python library
- **Regex Flags:** Supports Python regex flags (e.g., `re.IGNORECASE`)

## Installation

```bash
pip install rexplain
```

## Quick Start

### CLI Usage

Explain a regex pattern:
```bash
rexplain explain "^\d{3}-\d{2}-\d{4}$"
```

Generate example strings:
```bash
rexplain examples "[A-Za-z]{5}" --count 3
```

Test if a string matches a pattern:
```bash
rexplain test "^hello.*" "hello world!"
```

### Python API Usage

```python
from rexplain import explain, examples, test

print(explain(r"\d+"))
print(examples(r"[A-Z]{2}\d{2}", count=2))
print(test(r"foo.*", "foobar"))
```

#### Example: Detailed Explanation
```python
from rexplain import explain
print(explain(r"abc\w+\w*10$"))
# Output:
# a - matches the character 'a' (ASCII 97) literally (case sensitive)
# b - matches the character 'b' (ASCII 98) literally (case sensitive)
# c - matches the character 'c' (ASCII 99) literally (case sensitive)
# \w+ - matches a word character one or more times (greedy)
# \w* - matches a word character zero or more times (greedy)
# 1 - matches the character '1' (ASCII 49) literally (case sensitive)
# 0 - matches the character '0' (ASCII 48) literally (case sensitive)
# $ - asserts position at the end of a line
```

## API Reference

### `explain(pattern: str, flags: int = 0) -> str`
Returns a line-by-line explanation of the regex pattern.

### `examples(pattern: str, count: int = 3, flags: int = 0) -> List[str]`
Generates example strings that match the pattern.

### `test(pattern: str, test_string: str, flags: int = 0) -> dict`
Tests if a string matches the pattern and explains why/why not.

## Contributing

Contributions are welcome! To contribute:
- Fork the repo and create a branch
- Add or improve features/tests/docs
- Run tests
- Open a pull request

## License

MIT
