
# RAG System

## Description

This project is a Retrieval-Augmented Generation (RAG) system built with Flask, MongoDB, and transformers. It allows users to create, store, and search documents, leveraging state-of-the-art language models for generating responses to user queries.

## Setup

### Prerequisites

- Python 3.x
- MongoDB

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/rag-project.git
    cd rag-project
    ```

2. Create and activate a virtual environment:

    On Windows:

    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

    On Linux/macOS:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file in the project root directory and add the following variables:

    ```plaintext
    MONGO_URI=mongodb://localhost:27017/
    DB_NAME=queryDB
    COLLECTION_NAME=queries
    ```

5. Configure additional settings:

    Edit the `config.json` file in the project root directory to specify model configuration values:

    ```json
    {
      "model_name_or_path": "gpt2"
    }
    ```

### Running the Application

1. Ensure MongoDB is running:

    ```bash
    mongod
    ```

2. Run the Flask application:

    ```bash
    head "C:/Users/adiogoti/IdeaProjects/ragsystem/requirements.txt"
    ```

3. Access the application:

    Open your web browser and navigate to `http://127.0.0.1:5000/`.

## API Endpoints

### Create User

- **URL:** `/create_user`
- **Method:** `POST`
- **Payload:**

    ```json
    {
      "name": "John Doe"
    }
    ```

### Generate Response

- **URL:** `/generate`
- **Method:** `POST`
- **Payload:**

    ```json
    {
      "query": "What are the benefits of solar energy?"
    }
    ```

### Search Documents

- **URL:** `/search`
- **Method:** `POST`
- **Payload:**

    ```json
    {
      "query": "solar energy"
    }
    ```

### List Endpoints

- **URL:** `/list_endpoints`
- **Method:** `GET`

### Upload Document

- **URL:** `/upload_document`
- **Method:** `POST`
- **Payload:**

    Form-data with a file field named `file`.

### Example:

```bash
curl -F "file=@path/to/your/document.txt" http://127.0.0.1:5000/upload_document

```
## License

This project is licensed under the MIT License. See the LICENSE file for more details.