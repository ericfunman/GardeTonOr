import os

files = [
    "src/pages/dashboard.py",
    "src/pages/history.py",
    "src/pages/view_contracts.py",
    "tests/test_view_contracts.py"
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        cleaned_lines = [line.rstrip() + "\n" for line in lines]
        
        # Remove the extra newline at the end if the original file didn't have one, 
        # but flake8 usually wants one. rstrip() removes \n too, so we add it back.
        # Wait, rstrip() removes trailing \n. So line.rstrip() + "\n" is correct.
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
        print(f"Cleaned {file_path}")
    else:
        print(f"File not found: {file_path}")
