import os
import re
import argparse
import logging
from typing import List, Tuple, Dict

# Maximum number of tokens allowed in a PICO-8 project.
TOKEN_MAXIMUM: int = 8192

# Explicitly ignore certain tokens that are used programmatically but are not counted as tokens.
NON_TOKENS = {'end', ',', ')', '}', ']', ':'}

TOKEN_PATTERN = re.compile(r'"[^"]*"|\bnil\b|\bfalse\b|\btrue\b|\b\w+\b|\d+\.\d+|\d+|[\[\]{}()<>.,;:+=\-*/%~^#]|❎|⬆️|⬇️|⬅️|➡️')

KEYWORDS = {
    'if', 'then', 'else', 'elseif', 'while', 'do', 'for', 'in',
    'repeat', 'until', 'function', 'return', 'break'
}
OPERATORS = {
    '+', '-', '*', '/', '%', '^', '#', '=', '==', '+=', '-=',
    '>=', '<=', '~=', '<', '>', '..', 'and', 'or', 'not'
}
SYMBOLS = {'(', '[', '{'}
LITERALS = {'nil', 'false', 'true'}
SPECIALS = {'❎', '⬆️', '⬇️', '⬅️', '➡️'}


def merge_tokens(tokens: List[str]) -> List[str]:
    merged_tokens: List[str] = []
    i: int = 0

    operator_merge_map: Dict[Tuple[str, str], str] = {
        ('=', '='): '==',
        ('+', '='): '+=',
        ('-', '='): '-=',
        ('>', '='): '>=',
        ('<', '='): '<=',
    }

    negative_number_prefix_keywords = [
        'and', 'or', 'if', 'elseif', 'while', 'until',
        'return', 'not', 'local'
    ]
    negative_number_prefix_operators = [
        '+', '-', '*', '/', '%', '^', '^^', '=', '==', '!=', '+=', '-=',
        '>=', '<=', '~=', '<', '>', '.', '(', ')', '[', ']', '{', '}',
        ';', ':', ':=', ':==', '?', '&', '|'
    ]
    negative_number_prefix = negative_number_prefix_keywords + negative_number_prefix_operators

    while i < len(tokens):
        match tokens[i:]:
            case [a, '.', b, *_] if a.isdigit() and b.isdigit():
                merged_tokens.append(f'{a}.{b}')
                i += 3
            case [a, b, *_] if (a, b) in operator_merge_map:
                merged_tokens.append(operator_merge_map[(a, b)])
                i += 2
            case ['-', n, *_] if i >= 1 and n.isdigit() and tokens[i - 1] in negative_number_prefix:
                merged_tokens.append(f'-{n}')
                i += 2
            case [t, *_]:
                merged_tokens.append(t)
                i += 1

    return merged_tokens


def is_token(token: str) -> bool:
    if token in LITERALS | OPERATORS | SYMBOLS | KEYWORDS | SPECIALS:
        return True
    if token.isdigit() or token.startswith(('0x', '-')) or token.replace('.', '', 1).isdigit():
        return True
    if token.startswith(("'", '"')):
        return True
    if token.isidentifier() and token not in {'end', 'local'}:
        return True
    return False


def count_tokens_in_line(line: str) -> int:
    stripped = line.strip()
    if not stripped or stripped.startswith(("//", "--", "#")):
        return 0

    # Remove inline comments
    for sep in ("//", "--", "#"):
        line = line.split(sep)[0]

    tokens = TOKEN_PATTERN.findall(line)
    tokens = [token for token in tokens if token not in NON_TOKENS]
    merged_tokens = merge_tokens(tokens)
    return sum(1 for token in merged_tokens if is_token(token))


def count_tokens_in_file(file_path: str) -> int:
    with open(file_path, 'r') as file:
        content: str = file.read()

    content = content.replace("pico-8 cartridge // http://www.pico-8.com\nversion 36\n__lua__\n", "")
    content = re.sub(r'--\[\[.*?\]\]', '', content, flags=re.DOTALL)

    lines: List[str] = content.split('\n')
    total_tokens: int = sum(
        count_tokens_in_line(line) for line in lines
        if line.strip() and not line.strip().startswith('//')
    )

    return total_tokens


def count_tokens_in_directory(directory: str) -> Tuple[int, Dict[str, int]]:
    total_tokens: int = 0
    file_token_counts: Dict[str, int] = {}

    for filename in os.listdir(directory):
        if filename.endswith(".lua") and filename != "__gfx__.lua":
            file_path: str = os.path.join(directory, filename)
            file_tokens: int = count_tokens_in_file(file_path)
            file_token_counts[filename] = file_tokens
            total_tokens += file_tokens

    return total_tokens, file_token_counts


def format_token_summary(directory: str, total_tokens: int, file_token_counts: Dict[str, int]) -> None:
    max_name_len: int = max(len(filename) for filename in file_token_counts)
    max_count_len: int = max(len(str(count)) for count in list(file_token_counts.values()) + [total_tokens])

    logging.info(f"Token count per file in '{directory}':")
    logging.info('')

    for filename, count in sorted(file_token_counts.items()):
        padding: str = '-' * (max_name_len - len(filename) + 2)
        logging.info(f"  {filename}: {padding} {str(count).rjust(max_count_len)}")

    # Draw underline directly before summary
    line_width: int = max_name_len + 2 + 2 + max_count_len
    logging.info('  ' + '_' * (line_width + 1))

    # Token sum
    label_total: str = "Token sum"
    padding = '-' * (max_name_len - len(label_total) + 2)
    logging.info(f"  {label_total}: {padding} {str(total_tokens).rjust(max_count_len)}")
    logging.info('')

    # Final rows (max/remaining)
    label_1: str = "Maximum tokens"
    label_2: str = "Remaining tokens"
    pad_1: str = '-' * (max_name_len - len(label_1) + 2)
    pad_2: str = '-' * (max_name_len - len(label_2) + 2)

    logging.info(f"  {label_1}: {pad_1} {str(TOKEN_MAXIMUM).rjust(max_count_len)}")

    remaining: int = TOKEN_MAXIMUM - total_tokens
    percentage: float = 100 - (total_tokens / TOKEN_MAXIMUM * 100)
    logging.info(f"  {label_2}: {pad_2} {str(remaining).rjust(max_count_len)} ({percentage:.2f}%)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Token Counter for PICO-8 Lua files")
    parser.add_argument("directory", help="Directory containing Lua files")
    args = parser.parse_args()

    directory: str = args.directory
    total_tokens, file_token_counts = count_tokens_in_directory(directory)
    format_token_summary(directory, total_tokens, file_token_counts)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    main()