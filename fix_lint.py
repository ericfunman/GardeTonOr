import os

files = [
    r"c:\Users\lapin\OneDrive\Documents\Developpement\GardeTonOr\tests\test_openai_service_extended.py",
    r"c:\Users\lapin\OneDrive\Documents\Developpement\GardeTonOr\tests\test_pages.py",
    r"c:\Users\lapin\OneDrive\Documents\Developpement\GardeTonOr\tests\test_pages_coverage.py",
    r"c:\Users\lapin\OneDrive\Documents\Developpement\GardeTonOr\tests\test_pages_extended.py",
]


def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Remove trailing whitespace (fixes W291, W293)
        new_lines.append(line.rstrip() + "\n")

    # Join to string
    content = "".join(new_lines)

    # Ensure single newline at end (fixes W292, W391)
    content = content.rstrip() + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    for f in files:
        if os.path.exists(f):
            print(f"Fixing {f}")
            fix_file(f)
