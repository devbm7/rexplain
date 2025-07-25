# Examples

<!-- Example content for rexplain usage -->

## Regex Explanation

```python
from rexplain import explain
print(explain(r"abc\w+\w*10$"))
```

## Example String Generation

```python
from rexplain import examples
print(examples(r"[A-Z]{2}\d{2}", count=2))
```

## Regex Testing

```python
from rexplain import test
print(test(r"foo.*", "foobar"))
``` 