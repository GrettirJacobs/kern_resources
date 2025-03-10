"""
Tests for the Flask application endpoints and functionality.
"""

import pytest
import json
from pathlib import Path
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the main page route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'knowledge_graph' in response.data

def test_save_entry_endpoint(client):
    """Test the save_entry endpoint."""
    # Test successful save
    data = {
        'content': 'Test content for API endpoint',
        'title': 'Test Title'
    }
    response = client.post('/save_entry',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'entry_file' in result
    assert 'abstract_file' in result
    assert 'abstract' in result
    assert 'sentiment' in result
    assert 'tags' in result
    
    # Test empty content
    data = {
        'content': '',
        'title': 'Empty Test'
    }
    response = client.post('/save_entry',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test missing content
    data = {
        'title': 'Missing Content'
    }
    response = client.post('/save_entry',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400

def test_find_related_endpoint(client):
    """Test the find_related endpoint."""
    # First save some entries
    entries = [
        "Python is a versatile programming language",
        "Programming in Python is enjoyable",
        "JavaScript is used for web development"
    ]
    
    for entry in entries:
        data = {'content': entry}
        client.post('/save_entry',
                   data=json.dumps(data),
                   content_type='application/json')
    
    # Test finding related entries
    data = {
        'content': 'Python programming',
        'limit': 2
    }
    response = client.post('/find_related',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    results = json.loads(response.data)
    assert isinstance(results, list)
    assert len(results) <= 2
    
    # Test with missing content
    data = {'limit': 2}
    response = client.post('/find_related',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test with invalid limit
    data = {
        'content': 'test',
        'limit': 'invalid'
    }
    response = client.post('/find_related',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 500

def test_large_request_handling(client):
    """Test handling of large content requests."""
    # Generate a large piece of content
    large_content = "Test content " * 1000  # Approximately 12KB of text
    
    data = {
        'content': large_content,
        'title': 'Large Content Test'
    }
    response = client.post('/save_entry',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'entry_file' in result
    
    # Verify the content was saved correctly
    saved_content = Path(result['entry_file']).read_text()
    assert saved_content == large_content

def test_concurrent_requests(client):
    """Test handling of concurrent requests."""
    import concurrent.futures
    
    def make_request(i):
        data = {
            'content': f'Concurrent test content {i}',
            'title': f'Concurrent Test {i}'
        }
        return client.post('/save_entry',
                          data=json.dumps(data),
                          content_type='application/json')
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        responses = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # Check all requests were successful
    assert all(r.status_code == 200 for r in responses)
    
    # Check all responses have unique file paths
    results = [json.loads(r.data) for r in responses]
    entry_files = [r['entry_file'] for r in results]
    assert len(set(entry_files)) == 10  # All files should be unique
