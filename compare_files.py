import argparse

def compare_files(file1_path, file2_path):
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        line_number = 1
        for line1, line2 in zip(file1, file2):
            if line1 != line2:
                return f"Difference found at line {line_number}: \nFile 1: {line1.strip()}\nFile 2: {line2.strip()}"
            line_number += 1

        # Check if one file has more lines than the other
        if next(file1, None) or next(file2, None):
            return f"Difference found at line {line_number}: Files have different lengths."

    return "No differences found."

def main():
    parser = argparse.ArgumentParser(description="Compare two PICO-8 .p8 files and find the first discrepancy")
    parser.add_argument("file1", help="Path to the first .p8 file")
    parser.add_argument("file2", help="Path to the second .p8 file")
    args = parser.parse_args()

    result = compare_files(args.file1, args.file2)
    print(result)

if __name__ == "__main__":
    main()
