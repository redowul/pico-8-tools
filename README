# PICO-8 Code Management Tools

This project provides a set of Python scripts to manipulate PICO-8 .p8 files. The basic idea is to enable you to strip apart your .p8 file into lua files you can edit, and then use the `count_tokens.py` script to track token usage. When you're done, rebuild the .p8 file using `rebuild_p8_file.py` and it should be ready to be plugged right back into pico-8.

## Files & Usage

### split_p8_file.py

This script is used to split a PICO-8 .p8 file into separate Lua and gfx files. It reads the .p8 file line by line, and when it encounters a line starting with "--", it treats the rest of the line as the name of a new file. It writes all subsequent lines to that file, until it encounters another "--" line. The script also creates a new directory with the name of the project and places all the generated files in that directory.

To run `split_p8_file.py`, use the following command:

```
bash
python split_p8_file.py filename.p8
```

Replace filename.p8 with the name of your .p8 file.

### count_tokens.py

This script is used to count the number of tokens in PICO-8 Lua files within a specified directory. It uses the `argparse` module to parse command line arguments, specifically the directory containing the Lua files. The script counts the total number of tokens across all files in the directory, as well as the number of tokens in each individual file. It then prints these counts, along with the maximum number of tokens allowed for the project (8192), and the number and percentage of tokens remaining.

To run `count_tokens.py`, use the following command:

```bash
python count_tokens.py directory
```

Replace directory with the name of the directory containing your Lua files.

### rebuild_p8_file.py

This script is used to rebuild a PICO-8 .p8 file from separate Lua files in a directory. It reads a mapping file to determine the order of the Lua files, concatenates their contents, and writes the result to the output .p8 file. The script also appends the content of `__gfx__.lua` if it exists in the directory. The directory containing the Lua files and the name of the output .p8 file are specified as command line arguments.

To run `rebuild_p8_file.py`, use the following command:

```bash
python rebuild_p8_file.py directory output_filename.p8
```

Replace directory with the name of the directory containing your Lua files, and output_filename.p8 with the name you want for the output .p8 file.

#### Mapping File

The `rebuild_p8_file.py` script uses a mapping file to determine the order in which to concatenate the separate Lua files. This mapping file should be named `mappings.txt` and should be located in the same directory as the Lua files.

Each line in the mapping file should have the format `index:filename`, where `index` is a number indicating the order of the file, and `filename` is the name of the Lua file. The script reads the mapping file line by line, and for each line, it strips any leading or trailing whitespace and uses the remaining text as reference to know what file to open.

For example, a mapping file might look like this:

```
file_b.lua
file_a.lua
file_c.lua
```

In this case, the script would first concatenate the contents of `file_b.lua`, then `file_a.lua`, and finally `file_c.lua` because it works in line order.

Next, the script checks for a file named `__gfx__.lua` in the directory, and if it exists, appends its contents to the end of the output .p8 file.

### compare_files.py

This script is used to compare two PICO-8 .p8 files and find the first discrepancy between them. This is useful for verifying that the input of a .p8 file and the output of the unmodified directory created with `split_p8_file.py` produce the same end result. This ensures that we can make changes to the code in this terminal and receive a valid output later. The script reads both files line by line and returns the first line where they differ. If one file has more lines than the other, it also reports this discrepancy.

To run `compare_files.py`, use the following command:

```bash
python compare_files.py file1.p8 file2.p8
```

Replace file1.p8 and file2.p8 with the names of the .p8 files you want to compare.
