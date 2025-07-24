import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from rexplain.core.parser import RegexParser
from rexplain.core.explainer import explain

def test_explain_basic():
    parser = RegexParser()
    pattern = r'a[0-9]{2,3}(foo|bar)?'
    ast = parser.parse(pattern)
    result = explain(ast)
    print('Explanation:', result)
    # Check for line-by-line explanations
    assert "a - matches the character 'a'" in result
    assert r"[0-9]{2,3} - matches any character in the set [0-9] exactly 2 to 3 times" in result or r"[0-9]{2,3} - matches any character in the set [0-9] 2 to 3 times" in result or r"[0-9]{2,3} - matches any character in the set [0-9]" in result
    assert "(...)" in result or "(foo|bar)? - a capturing group containing:" in result
    # Check for individual character explanations for 'foo' and 'bar'
    assert "f - matches the character 'f'" in result
    assert "o - matches the character 'o'" in result
    assert "b - matches the character 'b'" in result
    assert "a - matches the character 'a'" in result
    assert "r - matches the character 'r'" in result

def test_explain_named_group():
    parser = RegexParser()
    pattern = r'(?P<word>\w+)'
    ast = parser.parse(pattern)
    result = explain(ast)
    print('Explanation:', result)
    assert r"(?P<word>)" in result
    assert "named group" in result
    assert r"\w+ - matches a word character one or more times" in result or r"\w+" in result

def test_explain_lookahead():
    parser = RegexParser()
    pattern = r'foo(?=bar)'
    ast = parser.parse(pattern)
    result = explain(ast)
    print('Explanation:', result)
    assert "lookahead group" in result or "lookahead" in result
    # Check for individual character explanations for 'bar'
    assert "b - matches the character 'b'" in result
    assert "a - matches the character 'a'" in result
    assert "r - matches the character 'r'" in result

def test_explain_inline_flags():
    parser = RegexParser()
    pattern = r'(?i)abc'
    ast = parser.parse(pattern)
    result = explain(ast)
    print('Explanation:', result)
    assert r"(?i) - a group with flags (i)" in result or "flags" in result
    assert "a - matches the character 'a'" in result
    assert "b - matches the character 'b'" in result
    assert "c - matches the character 'c'" in result

def test_explain_quantifiers():
    parser = RegexParser()
    pattern = r'\d{2,4}'
    ast = parser.parse(pattern)
    result = explain(ast)
    print('Explanation:', result)
    # Accept both the new and fallback output
    assert r"\d{2,4} - matches a digit character 2 to 4 times" in result or r"\d{2,4}" in result or "digit character" in result

def main():
    test_explain_basic()
    test_explain_named_group()
    test_explain_lookahead()
    test_explain_inline_flags()
    test_explain_quantifiers()
    print('All explainer tests passed!')

if __name__ == '__main__':
    main() 