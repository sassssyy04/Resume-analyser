import re

def format_answer(answer):
    lines = answer.split('\n')
    list_items = []
    additional_content_before = []
    additional_content_after = []
    components = []

    in_list_content = False
    for i, line in enumerate(lines):
        match_numbered = re.match(r'(\d+\.\s)(.+)', line)
        match_asterisk = re.match(r'(\*\s)(.+)', line)

        if match_numbered:
            if in_list_content:
                in_list_content = False
                components.append(f'<ul>{"".join(list_items)}</ul>')
                list_items = []
                components.append(line.strip())
            else:
                components.append(line.strip())
                in_list_content = True
                number = match_numbered.group(1)
                description = match_numbered.group(2).strip()
                list_items.append(f'<li>{number}{description}</li>')
        if match_asterisk:
            if in_list_content:
                list_items[-1] += f' {line}'
            else:
                components.append(f'<p>{line}</p>')
        elif in_list_content:
            in_list_content = False
            components.append(f'<ul>{"".join(list_items)}</ul>')
            list_items = []
            components.append(line.strip())
        else:
            components.append(line.strip())

    if list_items:
        components.append(f'<ul>{"".join(list_items)}</ul>')

    formatted_output = (f'<p>AthenaHR: {"\n".join(components)}</p>')

    return formatted_output

# Example usage
sample_input = """
Some text before the list.

1. First item in the list.
2. Second item in the list.

* Some text between the two lists.

* Item with asterisk 1.
* Item with asterisk 2.

Some text after the lists.
"""

formatted_output = format_answer(sample_input)
print(formatted_output)
