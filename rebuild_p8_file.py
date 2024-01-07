import os
import argparse

def rebuild_p8_file(directory, output_filename):
    mapping_file = os.path.join(directory, 'mappings.txt')

    if not os.path.exists(mapping_file):
        print(f"Mapping file not found in {directory}")
        return

    pico8_header = "pico-8 cartridge // http://www.pico-8.com\nversion 36\n__lua__\n"

    with open(mapping_file, 'r') as file:
        mappings = file.readlines()

    content = pico8_header

    for index, mapping in enumerate(mappings):
        file_name = mapping.strip()
        file_path = os.path.join(directory, file_name)

        with open(file_path, 'r') as file:
            file_content = file.read() #.rstrip()  # Remove trailing whitespace

            # Add file content
            content += file_content

    # Append __gfx__.lua if it exists
    gfx_file_path = os.path.join(directory, '__gfx__.lua')
    if os.path.exists(gfx_file_path):
        with open(gfx_file_path, 'r') as file:
            gfx_content = file.read()
            content += gfx_content

    # Write the content to the output file
    with open(output_filename, 'w') as file:
        file.write(content)

def main():
    parser = argparse.ArgumentParser(description="Rebuild a PICO-8 .p8 file from separate Lua files in a directory")
    parser.add_argument("directory", help="Directory containing the Lua files and mappings.txt")
    parser.add_argument("output_filename", help="Filename for the rebuilt .p8 file")
    args = parser.parse_args()

    rebuild_p8_file(args.directory, args.output_filename)

if __name__ == "__main__":
    main()
