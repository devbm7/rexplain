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

## Railroad Diagrams

### Basic Diagram Generation

```python
from rexplain import diagram

# Generate a simple diagram
svg_content = diagram(r"^\w+$")
print(svg_content[:100])  # Show first 100 characters

# Save diagram to file
diagram(r"^\w+$", "simple_diagram.svg")
```

### Detailed Diagram Generation

```python
from rexplain import diagram

# Generate a detailed diagram based on parsed components
diagram(r"^\w+@\w+\.\w+$", "email_diagram.svg", detailed=True)
```

### CLI Usage

```bash
# Generate basic diagram
rexplain diagram "^\\w+$" --output basic.svg

# Generate detailed diagram
rexplain diagram "^\\w+@\\w+\\.\\w+$" --detailed --output email.svg

# Print SVG to stdout
rexplain diagram "^\\d{3}-\\d{2}-\\d{4}$"
```

### Complex Pattern Examples

```python
from rexplain import diagram

# Email validation pattern
diagram(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", "email_validation.svg")

# Phone number pattern
diagram(r"^\(\d{3}\) \d{3}-\d{4}$", "phone_number.svg")

# Password validation pattern
diagram(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$", "password_validation.svg")
``` 