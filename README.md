# LEXI AI Chat Assistant with Knowledge Base Backend

This project implements a knowledge-based chat assistant using DeepSeek API. It allows users to create knowledge bases, add knowledge items, and get contextual responses to their questions based on the stored knowledge.

## Features

- Create and manage multiple knowledge bases
- Add, list, and delete knowledge items
- Embed text using Sentence Transformers
- Store metadata in PostgreSQL and vector embeddings in Pinecone
- Generate contextual responses using DeepSeek API
- RESTful API endpoints using Flask

## Prerequisites

- Python 3.12+
- PostgreSQL database
- Pinecone account (for vector database)
- DeepSeek API key

## Installation

### Using Pip and Virtual Environment

If you prefer using pip, you can install the dependencies using the traditional approach:

1. Clone this repository:

```bash
git clone git@github.com:BitBurstAlpha/ai-chatbot-backend.git
cd ai-chatbot-backend
```

2. Create a virtual environment and install dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On Unix/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

1. Start the Flask server:

```bash
python wsgi.py
```
