#!/usr/bin/env python3
"""Fix invalid JSON in translated batch files by escaping unescaped quotes."""
import json
import re
import sys

def fix_json_string(content):
    """Attempt to fix JSON with unescaped quotes inside string values."""
    # Strategy: parse character by character, tracking if we're inside a JSON string
    # When we encounter a quote that doesn't make sense structurally, escape it

    result = []
    i = 0
    in_string = False

    while i < len(content):
        ch = content[i]

        if not in_string:
            result.append(ch)
            if ch == '"':
                in_string = True
        else:
            if ch == '\\':
                # Escaped character - copy both
                result.append(ch)
                if i + 1 < len(content):
                    i += 1
                    result.append(content[i])
            elif ch == '"':
                # Is this the end of the string, or an unescaped quote in text?
                # Look ahead to determine
                rest = content[i+1:].lstrip()
                if (rest.startswith(',') or rest.startswith(']') or
                    rest.startswith('}') or rest.startswith(':') or
                    rest.startswith('\n') and (content[i+1:].lstrip().startswith(',') or
                                                content[i+1:].lstrip().startswith(']') or
                                                content[i+1:].lstrip().startswith('}'))):
                    # This looks like a structural closing quote
                    result.append(ch)
                    in_string = False
                else:
                    # This is probably an unescaped quote in text - escape it
                    result.append('\\')
                    result.append('"')
            else:
                result.append(ch)

        i += 1

    return ''.join(result)


def fix_file(filename):
    """Fix a single JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # First try to parse as-is
    try:
        data = json.loads(content)
        return True, len(data)
    except json.JSONDecodeError:
        pass

    # Try to fix
    fixed = fix_json_string(content)

    try:
        data = json.loads(fixed)
        # Write back
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True, len(data)
    except json.JSONDecodeError as e:
        # Try more aggressive fix: replace problematic patterns
        # German dialogue often uses „..." or "..." patterns
        # Try to fix by finding lines with odd number of unescaped quotes
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            stripped = line.strip()
            # Count unescaped quotes
            quote_count = 0
            j = 0
            while j < len(stripped):
                if stripped[j] == '\\' and j + 1 < len(stripped):
                    j += 2
                    continue
                if stripped[j] == '"':
                    quote_count += 1
                j += 1

            if quote_count > 2 and stripped.startswith('"'):
                # This line has too many quotes - try to fix by escaping inner ones
                # Find the opening and closing quotes
                inner = stripped[1:]  # skip first quote
                # Find last structural quote
                if inner.endswith('",') or inner.endswith('"'):
                    end_offset = 2 if inner.endswith('",') else 1
                    inner_content = inner[:-end_offset]
                    suffix = inner[-end_offset:]
                    # Escape all unescaped quotes in inner content
                    fixed_inner = inner_content.replace('\\"', '\x00').replace('"', '\\"').replace('\x00', '\\"')
                    fixed_line = line[:len(line)-len(stripped)] + '"' + fixed_inner + suffix
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        fixed2 = '\n'.join(fixed_lines)
        try:
            data = json.loads(fixed2)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True, len(data)
        except json.JSONDecodeError as e2:
            print(f"  Could not fix: {e2}")
            return False, 0


if __name__ == '__main__':
    import glob

    files = sorted(glob.glob('_small_batch_*_de.json'))
    fixed_count = 0
    failed_count = 0

    for f in files:
        success, num_sections = fix_file(f)
        if success:
            print(f"OK: {f} ({num_sections} sections)")
            fixed_count += 1
        else:
            print(f"FAILED: {f}")
            failed_count += 1

    print(f"\nResults: {fixed_count} OK, {failed_count} failed out of {len(files)} files")
