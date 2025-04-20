# DocAnatomyDemo - Intelligent Document Processing

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io)

## Features

- **Document Intelligence**: 
  - PDF parsing with configurable chunking (128-1024 chars)
  - Semantic search powered by FAISS
  - Metadata-preserving processing pipeline

- **AI Integration**:
  - Gemini 2.0 Flash for RAG responses
  - Hallucination-resistant output formatting
  - Context-aware summarization

- **Operational Tools**:
  - Dynamic re-indexing
  - Performance statistics tracking
  - Sample document suite for testing

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/DocAnatomyDemo.git
cd DocAnatomyDemo

# 2. Set up environment (Python 3.10 required)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch application
streamlit run main.py