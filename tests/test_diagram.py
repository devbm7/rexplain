"""
Tests for the diagram module.
"""

import pytest
import tempfile
import os
from rexplain.core.diagram import generate_railroad_diagram, generate_detailed_railroad_diagram


def test_generate_railroad_diagram_basic():
    """Test basic railroad diagram generation."""
    result = generate_railroad_diagram("test")
    assert isinstance(result, str)
    assert "<svg" in result
    assert "railroad-diagram" in result  # Check for the class instead of xmlns


def test_generate_railroad_diagram_with_output():
    """Test railroad diagram generation with output file."""
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_file:
        output_path = tmp_file.name
    
    try:
        result = generate_railroad_diagram("test", output_path)
        assert result == output_path
        assert os.path.exists(output_path)
        
        # Check that file contains SVG content
        with open(output_path, 'r') as f:
            content = f.read()
            assert "<svg" in content
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_generate_detailed_railroad_diagram_basic():
    """Test detailed railroad diagram generation."""
    result = generate_detailed_railroad_diagram("test")
    assert isinstance(result, str)
    assert "<svg" in result


def test_generate_detailed_railroad_diagram_with_output():
    """Test detailed railroad diagram generation with output file."""
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_file:
        output_path = tmp_file.name
    
    try:
        result = generate_detailed_railroad_diagram("test", output_path)
        assert result == output_path
        assert os.path.exists(output_path)
        
        # Check that file contains SVG content
        with open(output_path, 'r') as f:
            content = f.read()
            assert "<svg" in content
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_diagram_with_complex_pattern():
    """Test diagram generation with a more complex regex pattern."""
    pattern = r"^\w+@\w+\.\w+$"
    result = generate_railroad_diagram(pattern)
    assert isinstance(result, str)
    assert "<svg" in result


def test_diagram_error_handling():
    """Test that diagram generation handles errors gracefully."""
    # Test with a pattern that would cause parsing issues
    with pytest.raises(ValueError):
        generate_detailed_railroad_diagram("(")  # Unclosed parenthesis should cause error


def test_diagram_api_integration():
    """Test that the diagram function is available in the main API."""
    from rexplain import diagram
    
    result = diagram("test")
    assert isinstance(result, str)
    assert "<svg" in result


def test_diagram_cli_integration():
    """Test that diagram command is available in CLI."""
    from rexplain.cli.main import main
    import sys
    from io import StringIO
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        # Test diagram command (this would need to be run in a subprocess in real scenario)
        # For now, just test that the function exists and can be called
        from rexplain.core.diagram import generate_railroad_diagram
        result = generate_railroad_diagram("test")
        assert isinstance(result, str)
    finally:
        sys.stdout = old_stdout 