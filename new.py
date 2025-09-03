import os


def print_tree(start_path=".", prefix=""):
    # Get sorted list of items (directories first, then files)
    items = sorted(
        os.listdir(start_path),
        key=lambda s: (not os.path.isdir(os.path.join(start_path, s)), s.lower()),
    )

    for index, item in enumerate(items):
        path = os.path.join(start_path, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item)

        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            print_tree(path, prefix + extension)


if __name__ == "__main__":
    print(".")  
    print_tree(".")
