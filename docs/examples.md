# rexplain Examples

This page demonstrates how rexplain explains, tests, and generates examples for real-world regex patterns.

---

## Email Address

**Pattern:**
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

**Explanation:**
```
^ - asserts position at the start of a line
[a-zA-Z0-9._%+-]+ - matches any character in the set [a-zA-Z0-9._%+-] one or more times (greedy)
@ - matches the character '@' (ASCII 64) literally (case sensitive)
[a-zA-Z0-9.-]+ - matches any character in the set [a-zA-Z0-9.-] one or more times (greedy)
\. - matches the character '.' (ASCII 46) literally (case sensitive)
[a-zA-Z]{2,} - matches any character in the set [a-zA-Z] 2 to unlimited times
$ - asserts position at the end of a line
```

**Example Matches:**
- user@example.com
- hello.world+test@sub.domain.co

---

## US Phone Number

**Pattern:**
```
^\(\d{3}\) \d{3}-\d{4}$
```

**Explanation:**
```
^ - asserts position at the start of a line
\( - matches the character '(' (ASCII 40) literally (case sensitive)
\d{3} - matches a digit character exactly 3 times
\) - matches the character ')' (ASCII 41) literally (case sensitive)
  - matches the character ' ' (ASCII 32) literally (case sensitive)
\d{3} - matches a digit character exactly 3 times
- - matches the character '-' (ASCII 45) literally (case sensitive)
\d{4} - matches a digit character exactly 4 times
$ - asserts position at the end of a line
```

**Example Matches:**
- (123) 456-7890
- (555) 867-5309

---

## URL (Simple)

**Pattern:**
```
https?://[\w.-]+(?:\.[\w\.-]+)+[/\w\.-]*
```

**Explanation:**
```
h - matches the character 'h' (ASCII 104) literally (case sensitive)
t - matches the character 't' (ASCII 116) literally (case sensitive)
t - matches the character 't' (ASCII 116) literally (case sensitive)
p - matches the character 'p' (ASCII 112) literally (case sensitive)
s? - matches the character 's' (ASCII 115) zero or one time (greedy)
: - matches the character ':' (ASCII 58) literally (case sensitive)
/ - matches the character '/' (ASCII 47) literally (case sensitive)
/ - matches the character '/' (ASCII 47) literally (case sensitive)
[\w.-]+ - matches any character in the set [\w.-] one or more times (greedy)
(?:\.[\w\.-]+)+ - a non-capturing group containing:
  \. - matches the character '.' (ASCII 46) literally (case sensitive)
  [\w\.-]+ - matches any character in the set [\w\.-] one or more times (greedy)
  repeated one or more times (greedy)
[/\w\.-]* - matches any character in the set [/\w\.-] zero or more times (greedy)
```

**Example Matches:**
- http://example.com
- https://sub.domain.co.uk/path/to/page

---

## Password (At least 8 chars, 1 digit, 1 uppercase, 1 lowercase)

**Pattern:**
```
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$
```

**Explanation:**
```
^ - asserts position at the start of a line
(?=.*[a-z]) - a lookahead group (must be followed by) containing:
  .* - matches any character zero or more times (greedy)
  [a-z] - matches any character in the set [a-z]
(?=.*[A-Z]) - a lookahead group (must be followed by) containing:
  .* - matches any character zero or more times (greedy)
  [A-Z] - matches any character in the set [A-Z]
(?=.*\d) - a lookahead group (must be followed by) containing:
  .* - matches any character zero or more times (greedy)
  \d - matches a digit character
[A-Za-z\d]{8,} - matches any character in the set [A-Za-z\d] 8 to unlimited times
$ - asserts position at the end of a line
```

**Example Matches:**
- Password1
- Abcdefg8
- XyZ12345

---

## Date (YYYY-MM-DD)

**Pattern:**
```
^\d{4}-\d{2}-\d{2}$
```

**Explanation:**
```
^ - asserts position at the start of a line
\d{4} - matches a digit character exactly 4 times
- - matches the character '-' (ASCII 45) literally (case sensitive)
\d{2} - matches a digit character exactly 2 times
- - matches the character '-' (ASCII 45) literally (case sensitive)
\d{2} - matches a digit character exactly 2 times
$ - asserts position at the end of a line
```

**Example Matches:**
- 2023-01-01
- 1999-12-31 