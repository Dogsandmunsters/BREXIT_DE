#!/usr/bin/env python3
"""Assemble translated batch files into _sections_de.json and inject into index.html."""
import json
import sys

# 1. Merge all batch files
merged = {}
for i in range(1, 10):
    filename = f'_batch_{i}_de.json'
    try:
        with open(filename) as f:
            batch = json.load(f)
        print(f"Batch {i}: {len(batch)} sections loaded")
        merged.update(batch)
    except FileNotFoundError:
        print(f"ERROR: {filename} not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: {filename} has invalid JSON: {e}")
        sys.exit(1)

print(f"\nTotal sections merged: {len(merged)}")
if len(merged) != 865:
    print(f"WARNING: Expected 865 sections, got {len(merged)}!")

# 2. Validate structure - check a few sections have expected keys
sample_keys = ['1', '100', '500', '865']
for key in sample_keys:
    if key in merged:
        section = merged[key]
        print(f"Section {key} keys: {list(section.keys())}")

# 3. Write merged file
with open('_sections_de.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)
print(f"\nWrote _sections_de.json ({len(merged)} sections)")

# 4. Inject into index.html
with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the SECTIONS block boundaries
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'const SECTIONS = {' in line:
        start_line = i
    if start_line is not None and line.strip() == '};' and i > start_line + 10:
        end_line = i
        break

if start_line is None or end_line is None:
    print("ERROR: Could not find SECTIONS block in index.html!")
    sys.exit(1)

print(f"\nSECTIONS block found: lines {start_line+1} to {end_line+1}")

# Generate the new SECTIONS block
sections_json = json.dumps(merged, indent=2, ensure_ascii=False)
new_sections_block = f"        const SECTIONS = {sections_json};\n"

# Replace the old block
new_lines = lines[:start_line] + [new_sections_block] + lines[end_line+1:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

new_total = len(new_lines)
print(f"Wrote index.html ({new_total} lines)")
print("\nDone! Sections injected successfully.")
