import re

# Map: filename -> clean heading text
clean_titles = {
    "PLANNING.md": "Planning",
    "ANALYSIS.md": "Analysis",
    "DESIGN.md": "Design",
    "IMPLEMENTATION.md": "Implementation",
    "TESTING.md": "Testing",
    "DEPLOYMENT.md": "Deployment",
    "OPERATIONS_MAINTENANCE.md": "Operations & Maintenance",
}

for filename, clean_title in clean_titles.items():
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Skipped (not found): {filename}")
        continue

    # Replace the first H1 line (starts with "# ") with the clean title
    for i, line in enumerate(lines):
        if line.lstrip().startswith("# "):
            lines[i] = f"# {clean_title}\n"
            break

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Fixed heading in: {filename} -> # {clean_title}")

print("\nDone. Now rebuild with: make clean && make html (from the parent folder, not source)")
