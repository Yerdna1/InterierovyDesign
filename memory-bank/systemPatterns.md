# System Patterns

## System Architecture

- A single-script Streamlit application (`main.py`) that imports and uses PyTorch. (Inferred)
- Likely running within a Python virtual environment (`venv`).

## Key Technical Decisions

- Use of Streamlit for the frontend/UI layer.
- Use of PyTorch for backend processing/ML tasks.

## Design Patterns

- (None explicitly identified yet, likely a simple script structure initially).

## Component Relationships

- `main.py` (Streamlit App) --> `torch` (Library)

## Critical Implementation Paths

- Initialization of the Streamlit app.
- Import and potential use of `torch.classes` or related PyTorch modules that trigger the file watcher issue.

*This document outlines the inferred system structure and will be updated as understanding deepens.*
