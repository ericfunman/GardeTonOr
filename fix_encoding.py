import os

files = [
    "src/pages/add_contract.py",
    "src/pages/compare.py",
    "src/pages/view_contracts.py"
]

for file_path in files:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue

    try:
        with open(file_path, "rb") as f:
            content_bytes = f.read()
        
        if b"\x00" in content_bytes:
            print(f"File {file_path} contains null bytes. Fixing...")
            # It's likely mixed encoding (UTF-8 + UTF-16LE appended)
            # We can try to decode as utf-8 ignoring errors for the first part
            # and then handle the rest?
            # Or simpler: just remove null bytes if we assume it's all ASCII/Latin1 compatible code
            # But UTF-16 chars might be mangled.
            
            # PowerShell >> produces UTF-16 LE.
            # If the file was UTF-8, the new content is appended as bytes.
            # So we have UTF-8 bytes followed by UTF-16 LE bytes.
            
            # Let's try to find the BOM or just clean it up.
            # Since I only appended:
            # if __name__ == "__main__":
            #     show()
            # This is ASCII. So in UTF-16 LE it is: i\x00f\x00 ...
            # So removing \x00 should work for this specific case.
            
            clean_content = content_bytes.replace(b"\x00", b"")
            # Also remove BOM if present (\xff\xfe)
            clean_content = clean_content.replace(b"\xff\xfe", b"")
            
            text = clean_content.decode("utf-8")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Fixed {file_path}")
        else:
            print(f"File {file_path} is clean.")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
