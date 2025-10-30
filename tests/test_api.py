"""
Tests for the public API wrapper functions in __init__.py
"""
import sys
import os
import re
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import rexplain
from rexplain import explain, examples, diagram

def test_explain_api():
    """Test the explain() API function"""
    result = explain(r'\d+')
    assert isinstance(result, str)
    assert 'digit' in result.lower() or r'\d' in result

def test_explain_api_with_flags():
    """Test explain() with regex flags"""
    result = explain(r'abc', flags=re.IGNORECASE)
    assert isinstance(result, str)
    assert 'a' in result.lower()

def test_examples_api():
    """Test the examples() API function"""
    result = examples(r'[a-z]{3}', count=5)
    assert isinstance(result, list)
    assert len(result) == 5
    # Verify all examples match the pattern
    pattern = re.compile(r'[a-z]{3}')
    for ex in result:
        assert pattern.fullmatch(ex)

def test_examples_api_default_count():
    """Test examples() with default count"""
    result = examples(r'\d+')
    assert isinstance(result, list)
    assert len(result) == 3  # Default count

def test_examples_api_with_flags():
    """Test examples() with regex flags"""
    result = examples(r'[a-z]+', count=2, flags=re.IGNORECASE)
    assert isinstance(result, list)
    assert len(result) == 2

def test_test_api_match():
    """Test the test() API function with matching string"""
    result = rexplain.test(r'foo.*', 'foobar')
    assert hasattr(result, 'matches')
    assert result.matches is True
    assert result.reason

def test_test_api_no_match():
    """Test the test() API function with non-matching string"""
    result = rexplain.test(r'abc', 'xyz')
    assert hasattr(result, 'matches')
    assert result.matches is False
    assert result.reason

def test_test_api_with_flags():
    """Test test() with regex flags"""
    result = rexplain.test(r'abc', 'ABC', flags=re.IGNORECASE)
    assert result.matches is True

def test_diagram_api_basic():
    """Test the diagram() API function without output file"""
    result = diagram(r'\w+')
    assert isinstance(result, str)
    assert '<svg' in result

def test_diagram_api_with_output():
    """Test diagram() with output file"""
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
        output_path = tmp.name

    try:
        result = diagram(r'\d+', output_path=output_path)
        assert result == output_path
        assert os.path.exists(output_path)
        with open(output_path) as f:
            content = f.read()
            assert '<svg' in content
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)

def test_diagram_api_detailed():
    """Test diagram() with detailed flag"""
    result = diagram(r'\w+', detailed=True)
    assert isinstance(result, str)
    assert '<svg' in result

def test_diagram_api_detailed_with_output():
    """Test diagram() with detailed flag and output file"""
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
        output_path = tmp.name

    try:
        result = diagram(r'[a-z]+', output_path=output_path, detailed=True)
        assert result == output_path
        assert os.path.exists(output_path)
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)
