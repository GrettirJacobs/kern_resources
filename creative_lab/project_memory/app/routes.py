"""
Flask routes for Project Memory
"""

from flask import jsonify, request
from . import app, memory

@app.route('/')
def index():
    """Root endpoint that returns basic info about the API"""
    return jsonify({
        'status': 'ok',
        'message': 'Project Memory API is running'
    })

@app.route('/save_entry', methods=['POST'])
def save_entry():
    """Save a new memory entry"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
        
    if 'content' not in data:
        return jsonify({'error': 'Missing content field'}), 400
        
    if not data['content'] or not data['content'].strip():
        return jsonify({'error': 'Content cannot be empty'}), 400
    
    try:
        result = memory.save_entry(
            content=data['content'],
            title=data.get('title')
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/find_related', methods=['POST'])
def find_related():
    """Find related entries"""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query'}), 400
    
    try:
        results = memory.find_related_entries(data['query'])
        return jsonify(results)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/entries', methods=['GET'])
def get_entries():
    """Get all entries"""
    try:
        entries = memory.get_all_entries()
        return jsonify(entries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
