__version__ = "0.2.1"

from .core.explainer import RegexExplainer
from .core.generator import ExampleGenerator
from .core.tester import RegexTester

def explain(pattern: str, flags: int = 0) -> str:
    """Explain what a regex pattern does"""
    return RegexExplainer().explain(pattern, flags=flags)


def examples(pattern: str, count: int = 3, flags: int = 0):
    """Generate example strings that match the pattern"""
    return ExampleGenerator().generate(pattern, count, flags=flags)


def test(pattern: str, test_string: str, flags: int = 0):
    """Test if string matches pattern and explain why/why not"""
    result = RegexTester().test(pattern, test_string, flags=flags)
    return result