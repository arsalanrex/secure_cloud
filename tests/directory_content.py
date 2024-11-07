import os

# List of directories or files to exclude from traversal
excluded_items = [".venv", ".git", ".idea", ".DS_Store", "tests", "README.md"]


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
            with open(file_path, "r") as f:
                content = f.read()

            with open(output_file, "a") as out_f:
                out_f.write(f"\n{'=' * 40}\n")  # Divider
                out_f.write(f"File: {relative_path}\n")
                out_f.write(f"{'=' * 40}\n")
                out_f.write(content)
                out_f.write("\n\n")  # Extra newline after each file's content


# Define the base directory as the parent of the current directory (to get full project structure)
base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_file = os.path.join(os.path.dirname(__file__), "directory_content.txt")

# Clear any existing content in the output file before appending
open(output_file, "w").close()

# Read files and write their content to the output file
read_files(base_directory, output_file)

print(f"All file contents saved to {output_file}")
