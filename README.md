# rexplain

Explain, test, and generate examples for regular expressions.

## Installation

```bash
pip install .
```

## Usage

### CLI

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

### Python API

```python
from rexplain import explain, examples, test

print(explain(r"\d+"))
print(examples(r"[A-Z]{2}\d{2}", count=2))
print(test(r"foo.*", "foobar"))
```

## License
MIT 