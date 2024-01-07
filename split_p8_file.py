import os
import argparse

def split_p8_file(filename):
    project_name = os.path.splitext(filename)[0]

    # Check if the directory already exists
    if os.path.exists(project_name):
        print(f"Directory '{project_name}' already exists. Aborting to prevent overwriting.")
        return

    os.makedirs(project_name, exist_ok=True)

    # Initialize the mapping list
    mapping = []

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        current_file_name = 'initialization.lua'
        current_file_path = os.path.join(project_name, current_file_name)
        print(f"Creating file: {current_file_path}")
        current_file = open(current_file_path, 'w')

        for line_index, line in enumerate(lines):
            if line.startswith('__gfx__'):
                mapping.append(f"{current_file_name}")
                # Close the current file and start the gfx file
                current_file.close()
                current_file_name = '__gfx__.lua'
                current_file_path = os.path.join(project_name, current_file_name)
                print(f"Creating file: {current_file_path}")
                current_file = open(current_file_path, 'w')

            elif line.startswith('--#'):
                current_file.close()
                current_file_name = line[3:].strip() + '.lua'
                current_file_path = os.path.join(project_name, current_file_name)
                print(f"Creating file: {current_file_path}")
                current_file = open(current_file_path, 'w')

            elif line.startswith('-->8'):
                mapping.append(f"{current_file_name}")

            current_file.write(line)

        current_file.close()

        # Write the mappings to a file
        with open(os.path.join(project_name, 'mappings.txt'), 'w') as mapping_file:
            for m in mapping:
                mapping_file.write(m + '\n')

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Split a PICO-8 .p8 file into separate Lua and gfx files")
    parser.add_argument("filename", help="The .p8 file to split")
    args = parser.parse_args()

    split_p8_file(args.filename)

if __name__ == "__main__":
    main()
