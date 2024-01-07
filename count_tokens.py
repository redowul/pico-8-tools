import os
import re
import argparse
import logging

# Maximum number of tokens allowed in a PICO-8 project. Update this if the limit changes.
TOKEN_MAXIMUM = 8192

def merge_numeric_literals(tokens):
    merged_tokens = []
    i = 0

    while i < len(tokens):
        # Check if token is part of a numeric literal like '1.10'
        if i + 2 < len(tokens) and tokens[i].isdigit() and tokens[i + 1] == '.' and tokens[i + 2].isdigit():
            merged_tokens.append(tokens[i] + '.' + tokens[i + 2])
            i += 3  # Skip the next two tokens after merging
        else:
            merged_tokens.append(tokens[i])
            i += 1

    return merged_tokens


def merge_operator_tokens(tokens):
    merged_tokens = []
    i = 0

    while i < len(tokens):
        # Merge operator tokens if they exist in the merge_map
        merge_map = {
            ('=', '='): '==',
            ('+', '='): '+=',
            ('-', '='): '-=',
            ('>', '='): '>=',
            ('<', '='): '<=',
        }

        if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) in merge_map:
            merged_tokens.append(merge_map[(tokens[i], tokens[i + 1])])
            i += 2
        else:
            merged_tokens.append(tokens[i])
            i += 1

    return merged_tokens


def count_tokens_in_line(line):
    # Check if the line is empty or a comment
    if not line.strip() or line.strip().startswith('//') or line.strip().startswith('--') or line.strip().startswith('#'):
        return 0
    
    # Remove anything in the line after a comment
    line = line.split('//')[0].split('--')[0].split('#')[0]
    
    def is_token(token):
        token = token.strip()

        # Check if the token is a literal value
        if token in ['nil', 'false', 'true']:
            logging.info(f"{token} [1]")
            return True

        # Check if the token is a number
        if token.isdigit() or token.startswith(('0x', '-')) or token.replace('.', '', 1).isdigit():
            logging.info(f"{token} [2]")
            return True

        # Check if the token is a string
        if token.startswith(("'", '"')):
            logging.info(f"{token} [3]")
            return True

        # Check if the token is a variable or operator
        if (token.isidentifier() and token != 'end' and token != 'local') or token in ['+', '-', '*', '/', '%', '^', '#', '=', '==', "+=", "-=", ">=", "<=", '~=', '<', '>', '<=', '>=', '..', 'and', 'or', 'not']:
            logging.info(f"{token} [4]")
            return True

        # Check if the token is an opening bracket
        if token in ['(', '[', '{']:
            logging.info(f"{token} [5]")
            return True

        # Check if the token is a keyword (excluding end and local)
        if token in ['if', 'then', 'else', 'elseif', 'while', 'do', 'for', 'in', 'repeat', 'until', 'function', 'return', 'break']:
            logging.info(f"{token} [6]")
            return True
        
        # Check if the token is a button 
        if token in ['❎', '⬆️', '⬇️', '⬅️', '➡️']:
            logging.info(f"{token} [7]")
            return True

        return False

    # Regex pattern to split line into tokens
    # This pattern handles numeric literals, identifiers, and single-character operators
    token_pattern = r'\"[^\"]*\"|\bnil\b|\bfalse\b|\btrue\b|\b\w+\b|\d+\.\d+|\d+|[\[\]{}()<>.,;:+=\-*/%~^#]|❎|⬆️|⬇️|⬅️|➡️'

    # Split the line into tokens
    tokens = re.findall(token_pattern, line)

    # Merge numeric literals like '1.10'
    merged_tokens = merge_operator_tokens(merge_numeric_literals(tokens))

    # Count the tokens
    token_count = sum(1 for token in merged_tokens if is_token(token))
    return token_count 


def count_tokens_in_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Remove the specified lines from the top of the file
    content = content.replace("pico-8 cartridge // http://www.pico-8.com\nversion 36\n__lua__\n", "")

    # Strip out block comments
    content = re.sub(r'--\[\[.*?\]\]', '', content, flags=re.DOTALL)

    # Split content into lines
    lines = content.split('\n')

    # Initialize total token count
    total_tokens = 0

    # Iterate over each line and count tokens
    for line in lines:
        # Skip comments and empty lines
        if line.strip().startswith('//') or not line.strip():
            continue

        total_tokens += count_tokens_in_line(line)

    return total_tokens


def count_tokens_in_directory(directory):
    total_tokens = 0
    file_token_counts = {}

    for filename in os.listdir(directory):
        # Make sure filename is a Lua file and is not ""__gfx__.lua"
        if filename.endswith(".lua") and filename != "__gfx__.lua":
            file_path = os.path.join(directory, filename)
            file_tokens = count_tokens_in_file(file_path)
            file_token_counts[filename] = file_tokens
            total_tokens += file_tokens

    return total_tokens, file_token_counts


def main():
    parser = argparse.ArgumentParser(description="Token Counter for PICO-8 Lua files")
    parser.add_argument("directory", help="Directory containing Lua files")
    args = parser.parse_args()

    total_tokens, file_token_counts = count_tokens_in_directory(args.directory)

    print(f"Token count per file in '{args.directory}':")
    for filename, count in file_token_counts.items():
        print(f"  {filename}: {count}")

    print(f"Total tokens in the directory: {total_tokens}")
    print("Max tokens for project: 8192")
    print(f"Tokens remaining: {TOKEN_MAXIMUM - total_tokens}, or {100 - (total_tokens / TOKEN_MAXIMUM * 100):.2f}% of the total")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
