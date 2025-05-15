import sys
from scanner import Scanner
from parser import Parser

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file>")
        return

    input_file = sys.argv[1]

    scanner = Scanner(input_file)
    scanner.scan_file()

    print("=== Scanner Output ===")
    scanner.print_tokens()

    print("\n=== Parser Output ===")
    parser = Parser(scanner.tokens)
    parser.parse()

if __name__ == "__main__":
    main()
