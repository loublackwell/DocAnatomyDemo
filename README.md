# DocAnatomyDemo - Intelligent Document Processing

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![Public Domain](https://img.shields.io/badge/Texts-Public_Domain-brightgreen)](https://creativecommons.org/share-your-work/public-domain/)

## 📚 Project Description

DocAnatomyDemo is a **Retrieval-Augmented Generation (RAG) system** that transforms document collections into queryable knowledge bases. The application includes a curated library of public domain texts across multiple disciplines:

### Included Public Domain Texts
| Title | Author | Domain |
|-------|--------|--------|
| Computing Machinery and Intelligence | A.M. Turing | Computer Science |
| The Art of War | Sun Tzu | Military Strategy |
| Ministry of Healing | E.G. White | Health Sciences |
| The Great Controversy | E.G. White | Theology |

## 🖥️ Core Interface

<div align="center">
  <img src="images/search-ui.png" width="85%" alt="Main application interface showing query and results">
  <p><em>Search across documents with natural language queries</em></p>
</div>

## 🔍 Sample Query: Turing's Paper

<div align="center">
  <img src="images/app_querying.png" width="85%" alt="Example query showing technical answer extraction">
  <p><em>Precise answers with source citations</em></p>
  
  **Try This**:  
  `"How does Turing respond to the 'mathematical objection' to machine intelligence?"`
</div>

## ⚙️ Configuration Panel

<div align="center">
  <img src="images/reindexing.png" width="50%" alt="Document processing parameters">
  <p><em>Optimize retrieval with live parameter adjustment</em></p>
  
  **Key Settings**:
  - Chunk Size: 128-1024 characters  
  - Overlap: 10-25% of chunk size  
  - Top-K Results: 3-10 documents  
</div>


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
```

## 🚀 Future Roadmap

### Core Improvements
| Priority | Feature | Description |
|----------|---------|-------------|
| 🔴 High | **Text Cleaning Pipeline** | Advanced preprocessing for encoding issues (UTF-8 normalization, OCR artifact removal) |
| 🟠 Medium | **RAG Evaluation Suite** | Metrics for retrieval accuracy (Precision@K, MRR) and answer faithfulness |
| 🟢 Low | **Document Upload** | Drag-and-drop interface for user-provided PDFs |

### Extended Capabilities  
```python
planned_integrations = {
    "file_types": ["json", "csv", "docx", "pptx"],
    "multimodal": [
        "Image OCR extraction",
        "Chart data parsing", 
        "Audio transcription indexing"
    ]
}


## 💬 Contact Lewis Blackwell

<div align="center" style="margin: 1.5rem 0;">

[![Email](https://img.shields.io/badge/📧_Email-leblackwell.nlp@gmail.com-2CA5E0?logo=gmail&style=for-the-badge&logoColor=white)](mailto:leblackwell.nlp@gmail.com)
[![GitHub Issues](https://img.shields.io/badge/🐞_Report_Issues-GitHub-181717?logo=github&style=for-the-badge)](https://github.com/yourusername/DocAnatomyDemo/issues)

</div>

**I welcome communication about**:
- Usage questions
- Bug reports
- Feature suggestions