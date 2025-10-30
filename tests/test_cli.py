import subprocess
import sys
import os
import tempfile
import pytest
from unittest.mock import patch
from io import StringIO

def test_cli_help():
    cli_path = os.path.join(os.path.dirname(__file__), '../src/rexplain/cli/main.py')
    result = subprocess.run([sys.executable, cli_path, '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'usage:' in result.stdout.lower()

def test_cli_version():
    """Test --version flag"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', '--version'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 0
    assert result.stdout.strip()  # Should output version

def test_cli_about():
    """Test --about flag"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', '--about'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 0
    assert 'rexplain' in result.stdout.lower()

def test_cli_explain_basic():
    """Test explain command"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'explain', r'\d+'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 0
    assert 'digit' in result.stdout.lower() or r'\d' in result.stdout

def test_cli_explain_with_examples():
    """Test explain command with --examples flag"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'explain', r'\d{2}', '--examples', '2'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 0
    assert 'example' in result.stdout.lower()

def test_cli_examples():
    """Test examples command"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'examples', r'[a-z]{3}', '--count', '2'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 0
    lines = result.stdout.strip().split('\n')
    assert len(lines) >= 2  # Should have at least 2 examples

def test_cli_test_match():
    """Test test command with matching string"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'test', 'abc', 'abc'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 0

def test_cli_test_no_match():
    """Test test command with non-matching string"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'test', 'abc', 'xyz'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 1  # Should exit with error code

def test_cli_diagram_stdout():
    """Test diagram command without output file"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'diagram', r'\w+'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 0
    assert '<svg' in result.stdout

def test_cli_diagram_with_output():
    """Test diagram command with output file"""
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
        output_path = tmp.name

    try:
        result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'diagram', r'\w+', '--output', output_path],
                              capture_output=True, text=True, cwd='/home/user/rexplain/src')
        assert result.returncode == 0
        assert os.path.exists(output_path)
        with open(output_path) as f:
            content = f.read()
            assert '<svg' in content
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)

def test_cli_diagram_detailed():
    """Test diagram command with --detailed flag"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'diagram', r'\d+', '--detailed'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 0
    assert '<svg' in result.stdout

def test_cli_invalid_pattern():
    """Test CLI with invalid regex pattern"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main', 'explain', '(unclosed'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 1
    assert 'error' in result.stderr.lower() or 'error' in result.stdout.lower()

def test_cli_no_command():
    """Test CLI with no command shows help"""
    result = subprocess.run([sys.executable, '-m', 'rexplain.cli.main'],
                          capture_output=True, text=True, cwd='/home/user/rexplain/src')
    assert result.returncode == 1
    assert 'usage:' in result.stdout.lower() or 'usage:' in result.stderr.lower() 