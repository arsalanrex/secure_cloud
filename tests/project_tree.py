import os

# List of directories or files to exclude from the tree output
excluded_items = ["venv", ".git", ".idea", ".DS_Store", "tests", "README.md", "LICENSE", ".gitignore", ".pytest_cache"]


# Function to generate the directory tree, excluding specified items
def generate_tree(dir_path, prefix=""):
    tree_lines = []
    items = sorted(os.listdir(dir_path))  # Sort for consistent order

    for index, item in enumerate(items):
        # Skip items in the excluded list
        if item in excluded_items:
            continue

        path = os.path.join(dir_path, item)
        connector = "└── " if index == len(items) - 1 else "├── "

        # Append current item (file or directory)
        tree_lines.append(f"{prefix}{connector}{item}")

        # If the item is a directory, recursively add its contents
        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            tree_lines.extend(generate_tree(path, prefix=prefix + extension))

    return tree_lines


# Define the base directory as the parent of the current directory (tests)
base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_file = os.path.join(os.path.dirname(__file__), "project_tree.txt")

# Generate directory tree and write to output file in the tests directory
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(generate_tree(base_directory)))

print(f"Directory tree saved to {output_file}")
