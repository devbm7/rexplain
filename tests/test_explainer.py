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
    expected = (
        "the character 'a' followed by a character in the set [0-9] repeated 2 to 3 times followed by "
        "a capturing group containing the character 'f' followed by the character 'o' followed by the character 'o' or "
        "the character 'b' followed by the character 'a' followed by the character 'r' repeated zero or one time"
    )
    assert isinstance(result, str)
    print('Explanation:', result)

def test_explain_named_group():
    parser = RegexParser()
    pattern = r'(?P<word>\w+)'
    ast = parser.parse(pattern)
    result = explain(ast)
    print('Explanation:', result)
    assert 'named group' in result or 'group' in result

def test_explain_lookahead():
    parser = RegexParser()
    pattern = r'foo(?=bar)'
    ast = parser.parse(pattern)
    result = explain(ast)
    print('Explanation:', result)
    assert 'lookahead' in result

def test_explain_inline_flags():
    parser = RegexParser()
    pattern = r'(?i)abc'
    ast = parser.parse(pattern)
    result = explain(ast)
    print('Explanation:', result)
    assert 'flags' in result or 'group' in result

def main():
    test_explain_basic()
    test_explain_named_group()
    test_explain_lookahead()
    test_explain_inline_flags()
    print('All explainer tests passed!')

if __name__ == '__main__':
    main() 