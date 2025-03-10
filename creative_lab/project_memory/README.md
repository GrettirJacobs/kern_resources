# Project Memory System

A personal project management system that mimics human memory patterns by creating AI-generated abstractions of longer content while maintaining links to the original detailed information.

## Features

- Save detailed project entries, conversations, and notes
- Automatically generate abstracts using AI (BART-large-CNN model)
- Maintain links between abstracts and full content
- Clean, modern web interface
- Local storage of all content

## Requirements

- Python 3.8+
- Flask
- Transformers
- PyTorch
- NLTK
- Other dependencies listed in requirements.txt

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Enter your content in the text area
2. (Optional) Provide a title for your entry
3. Click "Save Entry" to store your content
4. The system will automatically generate an abstract
5. Browse your entries, with quick access to both abstracts and full content

## Storage

All content is stored locally in the `memory_store` directory:
- Full entries are stored in `memory_store/entries`
- Abstracts are stored in `memory_store/abstracts`

## Technical Details

- Uses BART-large-CNN model for abstractive summarization
- Implements chunking for handling long texts
- Stores metadata in JSON format
- Uses Flask for the web interface
