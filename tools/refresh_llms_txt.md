# LLM Documentation Refresh Prompt

Please update the llms/ directory with documentation for tools mentioned in Python.md.

## Process for Each Tool

### 1. CLI TOOLS
Run `{tool} --help` to get help output. Save to `llms/{tool}.txt`.

### 2. PYTHON PACKAGES
Check for official llms.txt files at common locations:
- https://docs.{package}.dev/latest/llms.txt or llms-full.txt
- https://{package}.readthedocs.io/llms.txt
- For pydantic-ai: https://ai.pydantic.dev/llms-full.txt
- For fasthtml: https://fastht.ml/docs/llms-ctx-full.txt

### 3. Documentation Footer
For each file, add a footer documenting:
- Source URL or command used
- Retrieval date
- Method (curl, help command, etc.)

## Requirements

- **IMPORTANT**: Only update existing files or create new ones for tools in Python.md
- Use curl to download llms.txt files when available
- For CLI tools not installed, create placeholder noting unavailability
- Include current date in documentation footer
- Preserve existing file structure and formatting when updating