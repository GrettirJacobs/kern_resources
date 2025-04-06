# Llama 4 Inference API

A Flask-based API service for running inference with Meta's Llama 4 Scout 17B E model.

## Prerequisites

- Python 3.10+
- CUDA-compatible GPU with sufficient VRAM (24GB+ recommended)
- Docker (optional)

## Local Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file with your configuration:
   ```
   MODEL_ID=meta-llama/Llama-4-Scout-17B-E
   PORT=5000
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t llama4-api .
   ```

2. Run the container:
   ```bash
   docker run --gpus all -p 5000:5000 llama4-api
   ```

## API Usage

### Health Check
```bash
curl http://localhost:5000/health
```

### Generate Text
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt here"}'
```

## Deployment

This application is designed to be deployed on GPU-enabled cloud platforms. Make sure to:
1. Configure appropriate GPU resources
2. Set up environment variables
3. Enable HTTPS for production deployments