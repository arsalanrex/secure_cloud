import os

# List of directories or files to exclude from traversal
excluded_items = [".venv", "venv", ".git", ".idea", ".DS_Store", "tests", "README.md", "LICENSE", "__pycache__", "__init__.py", ".gitignore"]


def read_files(dir_path, output_file):
    # Traverse the directory and process each file
    for root, dirs, files in os.walk(dir_path):
        # Modify `dirs` in-place to exclude unwanted directories during traversal
        dirs[:] = [d for d in dirs if d not in excluded_items]

        for file in files:
            # Skip excluded files
            if file in excluded_items:
                continue

            # Full path of the file
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, dir_path)

            # Read file content and write it to the output file with a header
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, "r", encoding="utf-8-sig") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, "r", encoding="ISO-8859-1") as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, "r", encoding="windows-1252") as f:
                                content = f.read()
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
                            continue

            with open(output_file, "a", encoding="utf-8") as out_f:
                out_f.write(f"\n{'=' * 40}\n")  # Divider
                out_f.write(f"File: {relative_path}\n")
                out_f.write(f"{'=' * 40}\n")
                out_f.write(content)
                out_f.write("\n\n")  # Extra newline after each file's content



# Define the base directory as the parent of the current directory (to get full project structure)
base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_file = os.path.join(os.path.dirname(__file__), "project_content.txt")

# Clear any existing content in the output file before appending
open(output_file, "w").close()

# Read files and write their content to the output file
read_files(base_directory, output_file)

print(f"All file contents saved to {output_file}")
