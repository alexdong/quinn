@README.md
@Python.md
@Makefile

## Available llms.txt Documentation

Some Python packages provide llms.txt files for better AI assistance. Known available sources:

### Confirmed Available:
- **FastHTML**: https://fastht.ml/docs/llms-ctx-full.txt (comprehensive XML context file)
- **Pydantic**: ai.pydantic.dev/llms-full.txt (pydantic-ai project)

### Tools for Converting Documentation:
- **LLM.codes**: Converts documentation from 69+ technical sites to LLM-friendly Markdown
- **llms_txt2ctx**: CLI tool to convert llms.txt to XML context documents

### Not Currently Available:
Most other Python packages (click, prompt-toolkit, rich, jinja2, numpy, plotly, streamlit, pytest, ruff) do not yet provide llms.txt files, though this may change as the standard gains adoption.

When llms.txt is not available, consider using the package's official documentation or tools like LLM.codes to create LLM-friendly versions.