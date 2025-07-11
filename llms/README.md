# llms.txt Documentation Collection

This directory contains llms.txt documentation status for Python packages used in this project.

## Summary

As of 2025-07-09, most Python packages have not yet adopted the llms.txt standard. Only FastHTML and Pydantic (via pydantic-ai) currently provide llms.txt documentation.

## Package Status

| Package | llms.txt Available | Notes |
|---------|-------------------|-------|
| pydantic | ⚠️ Partial | Available at ai.pydantic.dev/llms-full.txt |
| click | ❌ No | Official docs at click.palletsprojects.com |
| prompt-toolkit | ❌ No | Docs at python-prompt-toolkit.readthedocs.io |
| rich | ❌ No | Docs at rich.readthedocs.io |
| fasthtml | ✅ Yes | Available at fastht.ml/docs/llms-ctx-full.txt |
| jinja2 | ❌ No | Part of Pallets Projects |
| numpy | ❌ No | Docs at numpy.org |
| plotly | ❌ No | Docs at plotly.com/python/ |
| streamlit | ❌ No | Docs at docs.streamlit.io |
| pytest | ❌ No | Docs at docs.pytest.org |
| ruff | ❌ No | Docs at docs.astral.sh/ruff/ |

## About llms.txt

The llms.txt standard helps LLMs better understand and use website documentation. It consists of:
- **llms.txt**: An index file with links and brief descriptions
- **llms-full.txt**: All content in a single file
- **Markdown pages**: Clean versions of web pages (append .md to URLs)

## Alternatives

When llms.txt is not available:
1. Use LLM.codes to convert documentation to LLM-friendly format
2. Reference official documentation directly
3. Use the llms_txt2ctx tool to create XML context documents

## Retrieval Method

These files were created by searching for llms.txt documentation across package documentation sites. Direct fetching was limited due to domain restrictions, so WebSearch was used to determine availability.