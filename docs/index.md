# rexplain

Welcome to the documentation for **rexplain**!

rexplain is a Python toolkit for understanding, testing, and generating examples for regular expressions.

## Installation

```bash
pip install rexplain
```

## Features
- Regex explanation
- Example string generation
- Regex testing with feedback
- CLI and Python API

## Quick Start

### CLI
```bash
rexplain explain "^\d{3}-\d{2}-\d{4}$"
```

### Python API
```python
from rexplain import explain, examples, test
print(explain(r"\d+"))
print(examples(r"[A-Z]{2}\d{2}", count=2))
print(test(r"foo.*", "foobar"))
``` 