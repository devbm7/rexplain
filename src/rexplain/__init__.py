__version__ = "0.1.6"

from .core.explainer import RegexExplainer
from .core.generator import ExampleGenerator
from .core.tester import RegexTester

def explain(pattern: str) -> str:
    """Explain what a regex pattern does"""
    return RegexExplainer().explain(pattern)

def examples(pattern: str, count: int = 3):
    """Generate example strings that match the pattern"""
    return ExampleGenerator().generate(pattern, count)

def test(pattern: str, test_string: str):
    """Test if string matches pattern and explain why/why not"""
    result = RegexTester().test(pattern, test_string)
    return result