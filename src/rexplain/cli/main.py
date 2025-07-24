import argparse
import sys

# Import core functionality (update import paths if needed)
try:
    from rexplain.core.explainer import RegexExplainer
    from rexplain.core.generator import ExampleGenerator
    from rexplain.core.tester import RegexTester
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

def main():
    parser = argparse.ArgumentParser(description='Regex explanation toolkit')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # rexplain explain "pattern"
    explain_parser = subparsers.add_parser('explain', help='Explain a regex pattern')
    explain_parser.add_argument('pattern', help='Regex pattern to explain')

    # rexplain examples "pattern" --count 5
    examples_parser = subparsers.add_parser('examples', help='Generate example strings for a pattern')
    examples_parser.add_argument('pattern', help='Regex pattern to generate examples for')
    examples_parser.add_argument('--count', type=int, default=3, help='Number of examples to generate (default: 3)')

    # rexplain test "pattern" "string"
    test_parser = subparsers.add_parser('test', help='Test if a string matches a pattern')
    test_parser.add_argument('pattern', help='Regex pattern to test')
    test_parser.add_argument('string', help='String to test against the pattern')

    args = parser.parse_args()

    if args.command == 'explain':
        explainer = RegexExplainer()
        explanation = explainer.explain(args.pattern)
        print(explanation)
    elif args.command == 'examples':
        generator = ExampleGenerator()
        examples = generator.generate(args.pattern, args.count)
        for ex in examples:
            print(ex)
    elif args.command == 'test':
        tester = RegexTester()
        result = tester.test(args.pattern, args.string)
        # Assume result has a to_dict() method
        output = result.to_dict() if hasattr(result, 'to_dict') else result
        print(output)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 