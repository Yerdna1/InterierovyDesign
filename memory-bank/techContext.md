# Technical Context

## Technologies Used

- Python (version TBD, within `venv`)
- Streamlit (version TBD)
- PyTorch (version TBD)
- asyncio (implicitly used by Streamlit, potentially causing conflicts)

## Development Setup

- Local development environment on Windows 11.
- Using VS Code as the editor.
- Python virtual environment (`venv`) for managing dependencies.
- Dependencies listed in `requirements.txt`.

## Technical Constraints

- Must resolve the conflict between Streamlit's file watcher and PyTorch's class loading/introspection mechanisms.
- Compatibility between specific versions of Streamlit and PyTorch might be a factor.

## Dependencies

- Key dependencies: `streamlit`, `torch`. (Full list in `requirements.txt`).

## Tool Usage Patterns

- Running the application via `streamlit run main.py` (Assumed).

*This context details the technical stack and environment, subject to refinement.*
