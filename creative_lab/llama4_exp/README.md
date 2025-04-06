# Llama 4 Inference API

This is a Flask-based API service that runs inference with Meta's Llama 4 Scout 17B E model. The service is designed to be deployed in a GPU-enabled environment.

## Features

- Flask API with endpoints for health checks and text generation
- Lazy loading of the Llama 4 model to optimize memory usage
- Docker support with GPU acceleration
- Environment variable configuration
- Production-ready with Gunicorn server

## Requirements

- Python 3.10+
- CUDA-capable GPU
- Docker (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llama4-inference-api.git
cd llama4-inference-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
MODEL_ID=meta-llama/Llama-4-Scout-17B-E
PORT=5000
```

## Usage

### Running Locally

```bash
python app.py
```

### Running with Docker

```bash
docker build -t llama4-api .
docker run --gpus all -p 5000:5000 llama4-api
```

## API Endpoints

### Health Check
```
GET /health
```

### Generate Text
```
POST /generate
Content-Type: application/json

{
    "prompt": "Your text prompt here",
    "max_length": 100,
    "temperature": 0.7,
    "top_p": 0.9
}
```

## Deployment

The service is designed to be deployed on GPU-enabled cloud platforms. Make sure to:

1. Use a GPU-enabled instance
2. Set up proper CUDA drivers
3. Configure environment variables
4. Use proper security measures (API keys, rate limiting, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
