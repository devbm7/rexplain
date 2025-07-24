import subprocess
import sys
import os

def test_cli_help():
    cli_path = os.path.join(os.path.dirname(__file__), '../src/rexplain/cli/main.py')
    result = subprocess.run([sys.executable, cli_path, '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'usage:' in result.stdout.lower() 