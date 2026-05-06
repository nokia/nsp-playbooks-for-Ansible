#!/usr/bin/env python3
"""Auto-generate Ansible module documentation from docstrings.

This script parses Ansible module files and extracts DOCUMENTATION,
EXAMPLES, and RETURN sections to generate markdown documentation.
Implements DRY principle by pulling from source of truth (module code).

Uses Ansible documentation format standards:
- Synopsis: High-level overview
- Description: Detailed explanation with bullet points
- Requirements: External dependencies
- Parameters: Options with types, defaults, choices
- Examples: Real-world usage patterns
- Return Values: Output structure and types
- Notes: Important information
"""

import ast
import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from jinja2 import Environment, FileSystemLoader

# Use absolute path from project root
PROJECT_ROOT = Path(__file__).parent.parent
MODULE_DIR = PROJECT_ROOT / "plugins" / "modules"
PLUGINS_DIR = PROJECT_ROOT / "plugins"
DOCS_REFERENCE_DIR = PROJECT_ROOT / "docs" / "reference"
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Ansible doc markup: C()/V()/M()=code; I()=italic; B()=bold; O()/P()=param link; RV()=return link
_ANSIBLE_MACROS_CODE = frozenset('CVM')  # render as `...` (O, P, RV rendered as links)
_ANSIBLE_MACROS_ITALIC = frozenset('I')
_ANSIBLE_MACROS_BOLD = frozenset('B')

# Base URL for M(module) links to external Ansible docs (projects path)
_ANSIBLE_DOCS_BASE = "https://docs.ansible.com/projects/ansible/latest/collections"


def _find_matching_paren(text: str, start: int) -> int:
    """Return index of closing ')' matching '(' at start (exclusive)."""
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
        i += 1
    return i - 1 if depth == 0 else -1


def _param_anchor(name: str) -> str:
    """Return anchor for parameter link: param-<name> with underscores as dashes."""
    return "param-" + name.replace("_", "-")


def _return_anchor(name: str) -> str:
    """Return anchor for return value link: return-<name> with underscores as dashes."""
    return "return-" + name.replace("_", "-")


def ansible_format(text: Optional[str]) -> str:
    """Convert Ansible doc markup to Markdown.

    Supported macros:
    - C() -> `...` (code)
    - I() -> *...* (italic)
    - B() -> **...** (bold)
    - O(option) -> link to #param-option (option reference)
    - P(parameter) -> same as O() (legacy)
    - M(module) -> link to Ansible docs (module reference)
    - RV(return) -> link to #return-<key> (return value reference)
    - U(url) -> <url>
    - L(label, url) -> [label](url)
    - V() -> `...` (code, legacy)
    Handles nested parentheses inside macros.
    """
    if not text or not isinstance(text, str):
        return text or ''
    result = []
    i = 0
    while i < len(text):
        if i < len(text) - 2 and text[i + 1] == '(':
            macro = text[i]
            start = i + 2
            end = _find_matching_paren(text, start)
            if end < 0:
                result.append(text[i])
                i += 1
                continue
            inner = text[start:end]

            if macro == 'O' or macro == 'P':
                anchor = _param_anchor(inner)
                result.append(f"[`{inner}`](#{anchor})")
                i = end + 1
                continue
            if macro == 'RV':
                anchor = _return_anchor(inner)
                result.append(f"[`{inner}`](#{anchor})")
                i = end + 1
                continue
            if macro == 'U':
                result.append(f"<{inner}>")
                i = end + 1
                continue
            if macro == 'L':
                # L(label, url) -> [label](url); split on first ", "
                comma = inner.find(", ")
                if comma >= 0:
                    label = ansible_format(inner[:comma].strip())
                    url = inner[comma + 2:].strip()
                    result.append(f"[{label}]({url})")
                else:
                    result.append(f"`{inner}`")
                i = end + 1
                continue
            if macro == 'M':
                url = _module_doc_url(inner)
                formatted = ansible_format(inner)
                result.append(f"[{formatted}]({url})")
                i = end + 1
                continue
            if macro in _ANSIBLE_MACROS_CODE:
                result.append('`' + ansible_format(inner) + '`')
                i = end + 1
                continue
            if macro in _ANSIBLE_MACROS_ITALIC:
                result.append('*' + ansible_format(inner) + '*')
                i = end + 1
                continue
            if macro in _ANSIBLE_MACROS_BOLD:
                result.append('**' + ansible_format(inner) + '**')
                i = end + 1
                continue
        result.append(text[i])
        i += 1
    return ''.join(result)


# Setup Jinja2 environment and register Ansible format filter
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
jinja_env.filters['ansible'] = ansible_format


# Load configuration from galaxy.yml


def load_galaxy_config() -> Dict:
    """Load namespace, name, and collection FQCN from galaxy.yml."""
    galaxy_file = PROJECT_ROOT / "galaxy.yml"
    with open(galaxy_file, 'r') as f:
        galaxy_data = yaml.safe_load(f)
    namespace = galaxy_data.get('namespace', '')
    name = galaxy_data.get('name', '')
    return {
        'namespace': namespace,
        'name': name,
        'collection_fqcn': f"{namespace}.{name}" if namespace and name else '',
    }


CONFIG = load_galaxy_config()


def _module_doc_url(fqcn: str) -> str:
    """Return doc URL for M(module) FQCN: local reference for this collection, Ansible docs for ansible.*."""
    fqcn = fqcn.strip()
    parts = fqcn.split(".")
    if len(parts) < 3:
        return "#"
    name = parts[-1]

    # This collection (from galaxy.yml) → reference/<fqcn>.md (e.g. nokia.nsp.ibn.md)
    collection_fqcn = CONFIG.get('collection_fqcn', '')
    if collection_fqcn and fqcn.startswith(collection_fqcn + "."):
        return f"{fqcn}.md"

    # ansible.netcommon.* → collection index
    if fqcn.startswith("ansible.netcommon."):
        return f"{_ANSIBLE_DOCS_BASE}/ansible/netcommon/index.html"

    # ansible.builtin.<name> → module page
    if fqcn.startswith("ansible.builtin."):
        return f"{_ANSIBLE_DOCS_BASE}/ansible/builtin/{name}_module.html"

    # other ansible.<collection>.<name> → collection index
    if fqcn.startswith("ansible."):
        collection_path = "/".join(parts[1:-1])
        return f"{_ANSIBLE_DOCS_BASE}/ansible/{collection_path}/index.html"

    return "#"

# Plugin types to scan for documentation
PLUGIN_TYPES = [
    'httpapi',
    'cliconf',
    'netconf',
    'terminal',
    'connection',
    'module'  # Ensure modules are included if in plugins/
]


def extract_docstring_section(content: str, section: str) -> Optional[str]:
    """Extract DOCUMENTATION, EXAMPLES, or RETURN section from module code.

    Args:
        content: Module file content
        section: Section name (DOCUMENTATION, EXAMPLES, or RETURN)

    Returns:
        Extracted section content or None
    """
    # Use explicit delimiters so the opening quote is consumed (avoids matching it as
    # "closing" with (.*?) matching empty). Try triple-single-quote first, then triple-double.
    prefix = rf"{section}\s*=\s*r?"
    for delim in ("'''", '"""'):
        pattern = prefix + re.escape(delim) + r"(.*?)" + re.escape(delim)
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
    return None


def parse_yaml_doc(yaml_content: str) -> Dict:
    """Parse YAML documentation section into structured data.

    Args:
        yaml_content: Raw YAML documentation string

    Returns:
        Dictionary with parsed documentation
    """
    # Simple YAML parser for Ansible module docs
    data = {
        'module': None,
        'short_description': None,
        'description': None,
        'options': {},
        'version_added': None,
        'author': None,
        'notes': None,
    }

    lines = yaml_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith('module:'):
            data['module'] = line.split(':', 1)[1].strip()
        elif line.startswith('short_description:'):
            data['short_description'] = line.split(':', 1)[1].strip()
        elif line.startswith('version_added:'):
            data['version_added'] = line.split(':', 1)[1].strip()
        elif line.startswith('author:'):
            # Handle author list
            authors = []
            i += 1
            while i < len(lines) and lines[i].startswith('  - '):
                authors.append(lines[i].strip('- '))
                i += 1
            data['author'] = authors
            i -= 1

        i += 1

    return data


def extract_option_details(yaml_content: str) -> Dict[str, Dict]:
    """Parse module options from DOCUMENTATION block.

    Args:
        yaml_content: YAML documentation content

    Returns:
        Dictionary of options with their details
    """
    options = {}
    lines = yaml_content.split('\n')

    i = 0
    while i < len(lines):
        if lines[i].startswith('options:'):
            i += 1
            break
        i += 1

    current_option = None
    while i < len(lines):
        line = lines[i]

        # Stop at next top-level section
        if line and not line[0].isspace() and ':' in line:
            break

        # Parse option name (2 spaces indent)
        if line.startswith('  ') and not line.startswith('    ') and line.strip().endswith(':'):
            current_option = line.strip().rstrip(':')
            options[current_option] = {
                'description': [],
                'type': None,
                'required': False,
                'default': None,
                'choices': [],
                'aliases': []
            }

        # Parse option properties (4+ spaces indent)
        elif current_option and line.startswith('    '):
            stripped = line.strip()

            if stripped.startswith('description:'):
                # Could be multiline
                desc = stripped.split(':', 1)[1].strip()
                if desc:
                    options[current_option]['description'].append(desc)

            elif stripped.startswith('- '):
                # Bullet point in description or list
                if options[current_option]['description'] or not options[current_option].get('type'):
                    options[current_option]['description'].append(stripped)

            elif stripped.startswith('type:'):
                options[current_option]['type'] = stripped.split(':', 1)[1].strip()

            elif stripped.startswith('required:'):
                val = stripped.split(':', 1)[1].strip().lower()
                options[current_option]['required'] = val in ('true', 'yes')

            elif stripped.startswith('default:'):
                options[current_option]['default'] = stripped.split(':', 1)[1].strip()

            elif stripped.startswith('choices:'):
                i += 1
                while i < len(lines) and lines[i].startswith('      - '):
                    choice = lines[i].strip('- ').strip()
                    options[current_option]['choices'].append(choice)
                    i += 1
                i -= 1

            elif stripped.startswith('aliases:'):
                i += 1
                while i < len(lines) and lines[i].startswith('      - '):
                    alias = lines[i].strip('- ').strip()
                    options[current_option]['aliases'].append(alias)
                    i += 1
                i -= 1

        i += 1

    return options


def parse_return_block(return_content: Optional[str]) -> List[Dict]:
    """Parse RETURN block (Ansible return value docs) into structured list.

    Each entry has: key, description (str), returned (str), type (str), sample (optional).
    Top-level keys have 0 or 2 spaces indent; sub-keys have 4 spaces.
    """
    if not return_content or not return_content.strip():
        return []
    entries = []
    lines = return_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # Top-level key: "key:" or "  key:" (0 or 2 spaces), not "    subkey:"
        indent = len(line) - len(line.lstrip())
        is_key_line = stripped.endswith(':') and indent < 4 and ':' in line
        if is_key_line and stripped.rstrip(':').replace('_', '').isalnum():
            key = stripped.rstrip(':')
            if key:
                entry = {
                    'key': key,
                    'description': [],
                    'returned': None,
                    'type': None,
                    'sample': None,
                }
                i += 1
                while i < len(lines):
                    subline = lines[i]
                    if subline.strip() and len(subline) - len(subline.lstrip()) <= indent:
                        break
                    if subline.startswith('    ') or subline.startswith('  '):
                        sub = subline.strip()
                        if sub.startswith('description:'):
                            entry['description'].append(sub.split(':', 1)[1].strip())
                        elif sub.startswith('returned:'):
                            entry['returned'] = sub.split(':', 1)[1].strip()
                        elif sub.startswith('type:'):
                            entry['type'] = sub.split(':', 1)[1].strip()
                        elif sub.startswith('sample:'):
                            entry['sample'] = sub.split(':', 1)[1].strip()
                        elif sub.startswith('- ') and entry['description']:
                            entry['description'].append(sub)
                    i += 1
                entry['description_text'] = ' '.join(entry['description'])
                entries.append(entry)
                continue
        i += 1
    return entries


def format_sample_for_doc(sample) -> str:
    """Format a return value sample for documentation.

    If the sample is a string that is valid JSON (e.g. YAML-quoted JSON in
    RETURN block), parse it and return compact JSON so docs show native
    object representation without surrounding quotes.
    """
    if sample is None:
        return ""
    if isinstance(sample, str):
        stripped = sample.strip()
        if (stripped.startswith("'") and stripped.endswith("'")) or (
            stripped.startswith('"') and stripped.endswith('"')
        ):
            stripped = stripped[1:-1]
        try:
            parsed = json.loads(stripped)
            return json.dumps(parsed, separators=(",", ":"))
        except (json.JSONDecodeError, TypeError):
            pass
        return sample
    if isinstance(sample, (dict, list)):
        return json.dumps(sample, separators=(",", ":"))
    return str(sample)


def generate_doc_md(item_file: Path, item_type: str) -> str:
    """Generate markdown documentation for a module or plugin.

    Args:
        item_file: Path to Python file
        item_type: Type of item (module, httpapi, etc.)

    Returns:
        Generated markdown content
    """
    with open(item_file, 'r') as f:
        content = f.read()

    item_name = item_file.stem
    namespace = f"{CONFIG['namespace']}.{CONFIG['name']}.{item_name}"

    doc_section = extract_docstring_section(content, 'DOCUMENTATION')
    examples_section = extract_docstring_section(content, 'EXAMPLES')
    return_section = extract_docstring_section(content, 'RETURN')

    doc_data = parse_yaml_doc(doc_section) if doc_section else {}
    options = extract_option_details(doc_section) if doc_section else {}

    # Extract description items
    description_items = []
    if doc_section and 'description:' in doc_section:
        in_desc = False
        for line in doc_section.split('\n'):
            if 'description:' in line:
                in_desc = True
                continue
            if in_desc and line.strip().startswith('- '):
                description_items.append(line.strip()[2:])
            elif in_desc and line and not line[0].isspace():
                break

    # Extract notes
    notes = []
    if doc_section and 'notes:' in doc_section:
        in_notes = False
        for line in doc_section.split('\n'):
            if 'notes:' in line:
                in_notes = True
                continue
            if in_notes and line.strip().startswith('- '):
                notes.append(line.strip()[2:])
            elif in_notes and line and not line[0].isspace():
                break

    # Format options for template: build comments in Python (\\n -> <br/> in J2)
    formatted_options = {}
    for opt_name, opt_data in options.items():
        comments = []
        for line in opt_data.get('description', []):
            comments.append(ansible_format(line.lstrip('- ').strip()))

        if opt_data.get('choices'):
            choices_str = ", ".join(f"`{c}`" for c in opt_data['choices'])
            comments.append(f"**Choices:** {choices_str}")
        if opt_data.get('default') is not None:
            comments.append(f"**Default:** `{opt_data['default']}`")
        if opt_data.get('required', False):
            comments.append("**Required:** always")

        formatted_options[opt_name] = {
            'type': opt_data.get('type'),
            'required': opt_data.get('required', False),
            'default': opt_data.get('default'),
            "description": opt_data.get('description', []),
            'choices': opt_data.get('choices', []),
            'aliases': opt_data.get('aliases', []),
            'comments': "\n".join(comments),
        }

    # Parse RETURN block and format like Parameters: parameter, type, comments (aggregate)
    raw_return_entries = parse_return_block(return_section) if return_section else []
    return_entries = []
    for e in raw_return_entries:
        comments = []
        if e.get('description_text'):
            comments.append(ansible_format(e['description_text']))
        if e.get('returned'):
            comments.append(f"**Returned:** {ansible_format(e['returned'])}")
        if e.get('sample') is not None:
            comments.append(f"**Sample:** `{format_sample_for_doc(e['sample'])}`")
        return_entries.append({
            'key': e['key'],
            'type': e.get('type') or '-',
            'comments': "\n".join(comments) if comments else '-',
        })

    # Determine which template to use
    if item_type == 'module':
        template_name = 'module.md.j2'
    else:
        template_name = 'plugin.md.j2'

    # Render template
    template = jinja_env.get_template(template_name)
    return template.render(
        namespace=namespace,
        short_description=doc_data.get('short_description', item_name) or item_name,
        description_items=description_items,
        options=formatted_options,
        notes=notes,
        examples=examples_section,
        return_values=return_section,
        return_entries=return_entries,
        version_added=doc_data.get('version_added')
    )


def generate_all_docs():
    """Generate documentation for all modules and plugins."""
    DOCS_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    all_modules = []
    all_plugins = []

    # Generate module docs
    if MODULE_DIR.exists():
        module_files = sorted(MODULE_DIR.glob("*.py"))
        module_files = [m for m in module_files if not m.name.startswith("_")]

        collection_fqcn = CONFIG.get('collection_fqcn', '')
        for module_file in module_files:
            md_content = generate_doc_md(module_file, 'module')
            doc_name = f"{collection_fqcn}.{module_file.stem}.md" if collection_fqcn else f"module-{module_file.stem}.md"
            output_file = DOCS_REFERENCE_DIR / doc_name

            with open(output_file, 'w') as f:
                f.write(md_content)

            print(f"✓ Generated {output_file}")
            all_modules.append(module_file)

    # Generate plugin docs for each plugin type
    for plugin_type in PLUGIN_TYPES:
        plugin_dir = PLUGINS_DIR / plugin_type
        if not plugin_dir.exists():
            continue

        plugin_files = sorted(plugin_dir.glob("*.py"))
        plugin_files = [p for p in plugin_files if not p.name.startswith("_")]

        collection_fqcn = CONFIG.get('collection_fqcn', '')
        for plugin_file in plugin_files:
            md_content = generate_doc_md(plugin_file, plugin_type)
            doc_name = f"{collection_fqcn}.{plugin_file.stem}.md" if collection_fqcn else f"plugin-{plugin_file.stem}.md"
            output_file = DOCS_REFERENCE_DIR / doc_name

            with open(output_file, 'w') as f:
                f.write(md_content)

            print(f"✓ Generated {output_file}")
            all_plugins.append(plugin_file)

    return all_modules, all_plugins


def generate_combined_index(module_paths: List[Path], plugin_paths: List[Path]):
    """Generate combined index for all modules and plugins.

    Args:
        module_paths: List of module file paths
        plugin_paths: List of plugin file paths
    """
    # Build modules metadata
    modules_data = {}
    for module_file in module_paths:
        module_name = module_file.stem
        with open(module_file, 'r') as f:
            content = f.read()
        doc_section = extract_docstring_section(content, 'DOCUMENTATION')
        doc_data = parse_yaml_doc(doc_section) if doc_section else {}

        modules_data[module_name] = {
            'namespace': f"{CONFIG['namespace']}.{CONFIG['name']}.{module_name}",
            'description': doc_data.get('short_description', module_name) or module_name
        }

    # Build plugins metadata
    plugins_data = {}
    for plugin_file in plugin_paths:
        plugin_name = plugin_file.stem
        with open(plugin_file, 'r') as f:
            content = f.read()
        doc_section = extract_docstring_section(content, 'DOCUMENTATION')
        doc_data = parse_yaml_doc(doc_section) if doc_section else {}

        plugins_data[plugin_name] = {
            'namespace': f"{CONFIG['namespace']}.{CONFIG['name']}.{plugin_name}",
            'description': doc_data.get('short_description', plugin_name) or plugin_name
        }

    # Render template
    template = jinja_env.get_template('index.md.j2')
    content = template.render(
        modules=modules_data,
        plugins=plugins_data
    )

    index_file = DOCS_REFERENCE_DIR / "index.md"
    with open(index_file, 'w') as f:
        f.write(content)

    print(f"✓ Generated {index_file}")


def update_mkdocs_nav(module_paths: List[Path], plugin_paths: List[Path]):
    """Update mkdocs.yml nav section with Reference documentation.

    Args:
        module_paths: List of module file paths
        plugin_paths: List of plugin file paths
    """
    def format_display_name(name: str) -> str:
        """Format a filename to a display name.

        Converts snake_case to Title Case, preserving all-caps acronyms.
        Examples: rpc -> RPC, action -> Action, nsp -> NSP
        """
        parts = name.split('_')
        formatted_parts = []
        for part in parts:
            # If all uppercase (like "rpc" -> "RPC"), keep it uppercase
            if part.isupper() or (len(part) <= 3 and part.lower() in ['rpc', 'nsp', 'api']):
                formatted_parts.append(part.upper())
            else:
                formatted_parts.append(part.capitalize())
        return ' '.join(formatted_parts)

    mkdocs_file = PROJECT_ROOT / "mkdocs.yml"

    with open(mkdocs_file, 'r') as f:
        mkdocs_data = yaml.safe_load(f)

    # Build Reference navigation structure
    reference_nav = {
        'Reference': [
            {'Overview': 'reference/index.md'}
        ]
    }

    collection_fqcn = CONFIG.get('collection_fqcn', '')
    doc_ext = '.md'

    # Add Modules section if module_paths exist
    if module_paths:
        modules_nav = []
        for module_file in sorted(module_paths, key=lambda m: m.stem):
            module_name = module_file.stem
            display_name = format_display_name(module_name)
            doc_file = f"{collection_fqcn}.{module_name}{doc_ext}" if collection_fqcn else f"module-{module_name}{doc_ext}"
            modules_nav.append({display_name: f'reference/{doc_file}'})

        reference_nav['Reference'].append({'Modules': modules_nav})

    # Add Plugins section if plugin_paths exist
    if plugin_paths:
        plugins_nav = []
        for plugin_file in sorted(plugin_paths, key=lambda p: p.stem):
            plugin_name = plugin_file.stem
            display_name = format_display_name(plugin_name)
            doc_file = f"{collection_fqcn}.{plugin_name}{doc_ext}" if collection_fqcn else f"plugin-{plugin_name}{doc_ext}"
            plugins_nav.append({display_name: f'reference/{doc_file}'})

        reference_nav['Reference'].append({'Plugins': plugins_nav})

    # Find and replace Reference section in nav
    nav = mkdocs_data.get('nav', [])
    new_nav = []

    for item in nav:
        if isinstance(item, dict) and 'Reference' in item:
            # Replace Reference section
            new_nav.append(reference_nav)
        else:
            new_nav.append(item)

    mkdocs_data['nav'] = new_nav

    # Write back to mkdocs.yml
    with open(mkdocs_file, 'w') as f:
        yaml.dump(mkdocs_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✓ Updated {mkdocs_file}")


if __name__ == "__main__":
    print("Generating documentation from docstrings...\n")
    modules, plugins = generate_all_docs()
    print("\nIndex:")
    generate_combined_index(modules, plugins)
    print("\nNavigation:")
    update_mkdocs_nav(modules, plugins)
    print("\n✓ Documentation generation complete!")
