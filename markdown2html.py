#!/usr/bin/python3
"""
Markdown to HTML Converter
This script converts markdown syntax to HTML.
"""

import sys
import os
import re
import hashlib


def convert_headings(line):
    """Convert markdown headings to HTML headings."""
    match = re.match(r"^(#{1,6}) (.*)", line)
    if match:
        level = len(match.group(1))
        text = match.group(2)
        text = process_bold_emphasis(text)
        text = process_special_syntax(text)
        return f"<h{level}>{text}</h{level}>"
    return line


def process_bold_emphasis(text):
    """Convert **bold** to <b>bold</b> and __emphasis__ to <em>emphasis</em>"""
    # Process bold text
    bold_pattern = r"\*\*(.*?)\*\*"
    text = re.sub(bold_pattern, r"<b>\1</b>", text)

    # Process emphasis text
    emphasis_pattern = r"__(.*?)__"
    text = re.sub(emphasis_pattern, r"<em>\1</em>", text)

    return text


def process_md5(text):
    """Convert [[text]] to MD5 hash of text"""
    md5_pattern = r"\[\[(.*?)\]\]"

    def md5_replace(match):
        content = match.group(1)
        return hashlib.md5(content.encode()).hexdigest()

    return re.sub(md5_pattern, md5_replace, text)


def process_remove_c(text):
    """
    Convert ((text)) to text with all 'c'
    characters removed (case insensitive)
    """
    remove_c_pattern = r"\(\((.*?)\)\)"

    def remove_c_replace(match):
        content = match.group(1)
        return re.sub(r"[cC]", "", content)

    return re.sub(remove_c_pattern, remove_c_replace, text)


def process_special_syntax(text):
    """Process special syntax: MD5 conversion and character removal"""
    text = process_md5(text)
    text = process_remove_c(text)
    return text


def parse_markdown(input_file, output_file):
    """Parse markdown file and convert to HTML."""
    with open(input_file, "r") as f:
        content = f.read()

    lines = content.split("\n")
    html_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if it's a heading
        if line.startswith("#"):
            html_lines.append(convert_headings(line))
            i += 1

        # Check if it's an unordered list
        elif line.startswith("- "):
            ul_items = []
            while i < len(lines) and lines[i].startswith("- "):
                item = lines[i][2:]  # Remove the '- ' prefix
                item = process_bold_emphasis(item)
                item = process_special_syntax(item)
                ul_items.append(f"<li>{item}</li>")
                i += 1
            if ul_items:
                html_lines.append("<ul>")
                html_lines.extend(ul_items)
                html_lines.append("</ul>")

        # Check if it's an ordered list
        elif line.startswith("* "):
            ol_items = []
            while i < len(lines) and lines[i].startswith("* "):
                item = lines[i][2:]  # Remove the '* ' prefix
                item = process_bold_emphasis(item)
                item = process_special_syntax(item)
                ol_items.append(f"<li>{item}</li>")
                i += 1
            if ol_items:
                html_lines.append("<ol>")
                html_lines.extend(ol_items)
                html_lines.append("</ol>")

        # Check if it's a paragraph
        elif line.strip():
            para_lines = [line]
            i += 1
            # Collect all lines of the paragraph
            while (
                i < len(lines)
                and lines[i].strip()
                and not (
                    lines[i].startswith("#")
                    or lines[i].startswith("- ")
                    or lines[i].startswith("* ")
                )
            ):
                para_lines.append(lines[i])
                i += 1

            # Format paragraph
            html_lines.append("<p>")
            for j, para_line in enumerate(para_lines):
                processed_line = process_bold_emphasis(para_line)
                processed_line = process_special_syntax(processed_line)
                html_lines.append(processed_line)
                if j < len(para_lines) - 1:
                    html_lines.append("<br/>")
            html_lines.append("</p>")

        else:
            # Skip empty lines
            i += 1

    # Write the HTML content to the output file
    with open(output_file, "w") as f:
        f.write("\n".join(html_lines))


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        sys.stderr.write(f"Missing {input_file}\n")
        sys.exit(1)

    parse_markdown(input_file, output_file)
    sys.exit(0)


if __name__ == "__main__":
    main()
