"""
Project Memory System - Main Application File

This application implements a personal project management system that mimics human memory patterns.
It stores detailed content while creating AI-generated abstractions, similar to how human memory works
with recall cues and reconstruction.

The system uses Flask for the web interface, transformers for AI-powered summarization,
and incorporates features from popular open-source projects for enhanced functionality.
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
import json
from pathlib import Path
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import markdown
from app.enhanced_memory import EnhancedProjectMemory

# Initialize Flask application
app = Flask(__name__)

# Initialize the BART-large-CNN model for text summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Download the punkt tokenizer model from NLTK
nltk.download('punkt')

# Initialize enhanced memory system
memory_system = EnhancedProjectMemory(Path("memory_store"))

@app.route('/')
def index():
    """
    Render the main page of the application.
    Displays all entries with their abstracts in chronological order.
    """
    entries = []
    for abstract_file in memory_system.abstracts_path.glob("*_abstract.json"):
        with open(abstract_file) as f:
            entry_data = json.load(f)
            entries.append(entry_data)
    
    # Sort entries by timestamp (newest first)
    entries = sorted(entries, key=lambda x: x['timestamp'], reverse=True)
    
    # Generate knowledge graph
    knowledge_graph = memory_system.generate_knowledge_graph()
    
    return render_template('index.html', 
                         entries=entries,
                         knowledge_graph=knowledge_graph)

@app.route('/save_entry', methods=['POST'])
def save_entry():
    """
    Handle POST requests to save new entries.
    
    Expects JSON data with:
        - content: The main text content
        - title: (optional) Custom title for the entry
    
    Returns:
        JSON response with entry metadata or error message
    """
    content = request.json.get('content')
    title = request.json.get('title')
    
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    try:
        result = memory_system.save_entry(content, title)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/find_related', methods=['POST'])
def find_related():
    """
    Find entries related to the provided content.
    
    Expects JSON data with:
        - content: The content to find related entries for
        - limit: (optional) Number of related entries to return
    
    Returns:
        JSON response with related entries
    """
    content = request.json.get('content')
    limit = request.json.get('limit', 5)
    
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    try:
        related = memory_system.find_related_entries(content, top_n=limit)
        return jsonify(related)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
