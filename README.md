# DocAnatomyDemo - Intelligent Document Processing

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![Public Domain](https://img.shields.io/badge/Texts-Public_Domain-brightgreen)](https://creativecommons.org/share-your-work/public-domain/)

## 📚 Project Description

DocAnatomyDemo is a **Retrieval-Augmented Generation (RAG) system** that transforms document collections into queryable knowledge bases. The application includes **a curated library of public domain works** for legal experimentation and analysis:

### Public Domain Text Library
| Title | Author | Year | Domain | PD Status |
|-------|--------|------|--------|-----------|
| [Computing Machinery and Intelligence](https://www.csee.umbc.edu/courses/471/papers/turing.pdf) | A.M. Turing | 1950 | Computer Science | [PD worldwide](https://commons.wikimedia.org/wiki/File:On_Computable_Numbers,_with_an_Application_to_the_Entscheidungsproblem.pdf) |
| The Art of War | Sun Tzu | 5th c. BCE | Military Strategy | [PD by age](https://en.wikipedia.org/wiki/The_Art_of_War#Copyright_status) |
| Ministry of Healing | E.G. White | 1905 | Health Sciences | [PD in US](https://copyright.cornell.edu/publicdomain) |
| The Great Controversy | E.G. White | 1888 | Theology | [PD in US](https://copyright.cornell.edu/publicdomain) |

**Public Domain Verification**:
```bash
# Copyright status check (US)
current_year=$(date +'%Y')
if [ $((current_year - publication_year)) -ge 95 ]; then
  echo "Likely public domain in US"
fi
```

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