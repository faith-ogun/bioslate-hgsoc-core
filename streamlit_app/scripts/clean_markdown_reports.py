import os

REPORTS_DIR = "streamlit_app/reports"

def clean_fenced_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx, end_idx = None, None
    for i, line in enumerate(lines):
        if line.strip() == "```markdown" and start_idx is None:
            start_idx = i
        elif line.strip() == "```" and start_idx is not None:
            end_idx = i
            break

    if start_idx is not None and end_idx is not None and start_idx < end_idx:
        cleaned_lines = lines[start_idx + 1:end_idx]
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
        return True

    return False

def clean_all_reports():
    cleaned_count = 0
    for fname in os.listdir(REPORTS_DIR):
        if fname.endswith(".md"):
            path = os.path.join(REPORTS_DIR, fname)
            if clean_fenced_markdown(path):
                cleaned_count += 1
                print(f"Cleaned: {fname}")
    print(f"\nDone. Cleaned {cleaned_count} Markdown files.")

if __name__ == "__main__":
    clean_all_reports()
