import sys
import os
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from rexplain.core.generator import ExampleGenerator

def assert_examples_match(pattern, examples):
    prog = re.compile(pattern)
    for ex in examples:
        assert prog.fullmatch(ex), f"Example '{ex}' does not match pattern '{pattern}'"

def test_literal():
    gen = ExampleGenerator()
    pattern = 'abc'
    examples = gen.generate(pattern, 5)
    assert_examples_match(pattern, examples)

def test_char_class():
    gen = ExampleGenerator()
    pattern = '[a-c]'
    examples = gen.generate(pattern, 10)
    assert_examples_match(pattern, examples)

    pattern = '[^a-c]'
    examples = gen.generate(pattern, 10)
    assert_examples_match(pattern, examples)

def test_escape():
    gen = ExampleGenerator()
    pattern = r'\d\w\s'
    examples = gen.generate(pattern, 10)
    assert_examples_match(pattern, examples)

def test_quantifier():
    gen = ExampleGenerator()
    pattern = 'a{2,4}'
    examples = gen.generate(pattern, 10)
    assert_examples_match(pattern, examples)

    pattern = 'b*'
    examples = gen.generate(pattern, 10)
    assert_examples_match(pattern, examples)

def test_alternation():
    gen = ExampleGenerator()
    pattern = 'foo|bar'
    examples = gen.generate(pattern, 10)
    assert_examples_match(pattern, examples)

def test_group():
    gen = ExampleGenerator()
    pattern = '(ab)+'
    examples = gen.generate(pattern, 10)
    assert_examples_match(pattern, examples)

def test_nested():
    gen = ExampleGenerator()
    pattern = '(a[0-9]|b[xyz]){2}'
    examples = gen.generate(pattern, 10)
    assert_examples_match(pattern, examples)

def test_unicode_hex():
    gen = ExampleGenerator()
    pattern = r'\u0061\x62'  # 'a' and 'b'
    examples = gen.generate(pattern, 5)
    assert_examples_match('ab', examples)

def test_edge_cases():
    gen = ExampleGenerator()
    pattern = ''
    examples = gen.generate(pattern, 3)
    assert_examples_match(pattern, examples)

    pattern = '^abc$'
    examples = gen.generate(pattern, 3)
    assert_examples_match('abc', examples)

def main():
    test_literal()
    print('test_literal passed')
    test_char_class()
    print('test_char_class passed')
    test_escape()
    print('test_escape passed')
    test_quantifier()
    print('test_quantifier passed')
    test_alternation()
    print('test_alternation passed')
    test_group()
    print('test_group passed')
    test_nested()
    print('test_nested passed')
    test_unicode_hex()
    print('test_unicode_hex passed')
    test_edge_cases()
    print('test_edge_cases passed')
    print('All generator tests passed!')

if __name__ == '__main__':
    main() 