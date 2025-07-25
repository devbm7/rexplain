import argparse
import sys
import os

# Import core functionality (update import paths if needed)
try:
    from rexplain.core.explainer import RegexExplainer
    from rexplain.core.generator import ExampleGenerator
    from rexplain.core.tester import RegexTester
    from rexplain import __version__
except ImportError as e:
    print("IMPORT ERROR:", e, file=sys.stderr)
    # Stubs for development if core modules are missing
    class RegexExplainer:
        def explain(self, pattern):
            return f"[Stub] Explanation for: {pattern}"
    class ExampleGenerator:
        def generate(self, pattern, count=3):
            return [f"example_{i+1}" for i in range(count)]
    class RegexTester:
        def test(self, pattern, string):
            return type('Result', (), {"matches": True, "reason": "[Stub] Always matches", "to_dict": lambda self: {"matches": True, "reason": "[Stub] Always matches"}})()
    __version__ = "unknown"

PROJECT_ABOUT = (
    "rexplain: Explain, test, and generate examples for regular expressions. "
    "A Python toolkit for understanding, testing, and generating examples for regex. "
    "Features: line-by-line explanations, example generation, detailed match testing, CLI & API."
)

def main():
    parser = argparse.ArgumentParser(
        description='rexplain: Regex explanation toolkit',
        epilog='Examples:\n  rexplain explain "^\\d{3}-\\d{2}-\\d{4}$" --examples 2\n  rexplain test "foo.*" "foobar"\n  rexplain --version\n  rexplain --about',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    parser.add_argument('--about', action='store_true', help='Show project description and exit')

    subparsers = parser.add_subparsers(dest='command', required=False)

    # rexplain explain "pattern"
    explain_parser = subparsers.add_parser('explain', help='Explain a regex pattern')
    explain_parser.add_argument('pattern', help='Regex pattern to explain')
    explain_parser.add_argument('--examples', type=int, default=0, help='Show N example matches for the pattern')

    # rexplain examples "pattern" --count 5
    examples_parser = subparsers.add_parser('examples', help='Generate example strings for a pattern')
    examples_parser.add_argument('pattern', help='Regex pattern to generate examples for')
    examples_parser.add_argument('--count', type=int, default=3, help='Number of examples to generate (default: 3)')

    # rexplain test "pattern" "string"
    test_parser = subparsers.add_parser('test', help='Test if a string matches a pattern')
    test_parser.add_argument('pattern', help='Regex pattern to test')
    test_parser.add_argument('string', help='String to test against the pattern')

    args = parser.parse_args()

    # Handle global flags
    if args.version:
        print(__version__)
        sys.exit(0)
    if args.about:
        print(PROJECT_ABOUT)
        sys.exit(0)
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'explain':
            explainer = RegexExplainer()
            explanation = explainer.explain(args.pattern)
            print(explanation)
            if getattr(args, 'examples', 0) > 0:
                generator = ExampleGenerator()
                print(f"\nExample matches:")
                for ex in generator.generate(args.pattern, args.examples):
                    print(f"  {ex}")
            sys.exit(0)
        elif args.command == 'examples':
            generator = ExampleGenerator()
            examples = generator.generate(args.pattern, args.count)
            for ex in examples:
                print(ex)
            sys.exit(0)
        elif args.command == 'test':
            tester = RegexTester()
            result = tester.test(args.pattern, args.string)
            output = result.to_dict() if hasattr(result, 'to_dict') else result
            print(output)
            sys.exit(0 if getattr(result, 'matches', False) else 1)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 