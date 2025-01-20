import requests
import pytest
import time
import os

# Base URL for the API - configurable via environment variables
API_HOST = os.getenv('API_HOST', 'localhost')
API_PORT = os.getenv('API_PORT', '5002')  # Default to Docker port
API_URL = f"http://{API_HOST}:{API_PORT}"

print(f"Running tests against API at: {API_URL}")

@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Wait for API to be ready before running tests"""
    max_retries = 30
    retry_interval = 1

    for _ in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/api/v1/endpoints")
            if response.status_code == 200:
                print("API is ready!")
                return
        except requests.exceptions.ConnectionError:
            print("Waiting for API to be ready...")
            time.sleep(retry_interval)
    
    pytest.fail("API did not become ready in time")

def test_endpoints_listing():
    """Test the endpoints listing endpoint"""
    response = requests.get(f"{API_URL}/api/v1/endpoints")
    assert response.status_code == 200
    
    data = response.json()
    assert "endpoints" in data
    
    # Verify essential endpoints exist
    endpoints = [endpoint["url"] for endpoint in data["endpoints"]]
    essential_paths = [
        "/api/v1/search",
        "/api/v1/generate",
        "/api/v1/documents"
    ]
    for path in essential_paths:
        assert any(path in endpoint for endpoint in endpoints), f"Missing endpoint: {path}"

def test_search_endpoint():
    """Test the search endpoint"""
    test_query = {
        "query": "create_user",
        "include_sentiment": True
    }
    
    response = requests.post(
        f"{API_URL}/api/v1/search",
        json=test_query
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "results" in data
    assert "document_results" in data["results"]

def test_generate_endpoint():
    """Test the generate endpoint"""
    test_query = {
        "query": "How do I create a user?"
    }
    
    response = requests.post(
        f"{API_URL}/api/v1/generate",
        json=test_query
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "response" in data
    assert data["response"]

def test_document_operations():
    """Test document upload and retrieval"""
    # List existing files
    list_response = requests.get(f"{API_URL}/api/v1/documents")
    print("\nExisting files in GridFS:")
    print(list_response.json())
    
    # Test file upload
    test_content = b'This is a test document content'
    files = {
        'file': ('test.txt', test_content, 'text/plain')
    }
    
    # Upload file
    upload_url = f"{API_URL}/api/v1/documents"
    print(f"\nPOST Request to: {upload_url}")
    print(f"Files data: {files}")
    
    upload_response = requests.post(upload_url, files=files)
    print(f"Upload Response Status: {upload_response.status_code}")
    print(f"Upload Response Headers: {dict(upload_response.headers)}")
    print(f"Upload Response Body: {upload_response.text}")
    
    assert upload_response.status_code == 201, f"Upload failed: {upload_response.text}"
    
    data = upload_response.json()
    assert "file_id" in data, "No file_id in response"
    file_id = data["file_id"]
    
    print(f"\nUploaded file_id: {file_id}")
    print(f"Response data: {data}")
    
    # List files after upload
    list_response = requests.get(f"{API_URL}/api/v1/documents")
    print("\nFiles after upload:")
    print(list_response.json())
    
    # Verify file_id is a valid ObjectId
    assert len(file_id) == 24, f"Invalid file_id format: {file_id}"
    
    # Test document retrieval
    get_url = f"{API_URL}/api/v1/documents/{file_id}"
    print(f"\nGET Request to: {get_url}")
    
    get_response = requests.get(get_url)
    print(f"GET Response Status: {get_response.status_code}")
    print(f"GET Response Headers: {dict(get_response.headers)}")
    print(f"GET Response Body: {get_response.text}")
    
    assert get_response.status_code == 200, f"Failed to retrieve document. Response: {get_response.text}"
    
    content = get_response.json()
    assert "content" in content, "No content in response"
    assert "filename" in content, "No filename in response"
    assert content["filename"] == "test.txt"
    assert "test document content" in content["content"] 