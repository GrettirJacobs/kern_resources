# Google Colab Implementation for Llama 4

This directory contains a Jupyter notebook for running Llama 4 models on Google Colab with A100 GPU and exposing them via an API endpoint.

## Overview

The `llama4_ollama_api.ipynb` notebook sets up:

1. Ollama running on Google Colab
2. Llama 4 Scout Instruct model
3. Flask API server
4. ngrok tunnel for external access

This approach allows you to leverage the powerful A100 GPUs available in Google Colab Pro ($9.99/month) to run Llama 4 models without the high cost of dedicated GPU instances.

## Usage Instructions

### 1. Open the Notebook in Google Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Upload the `llama4_ollama_api.ipynb` notebook
3. Make sure you have Colab Pro for reliable A100 GPU access

### 2. Run the Notebook

1. Select "Runtime" > "Change runtime type"
2. Set "Hardware accelerator" to "GPU"
3. Run each cell in sequence
4. When prompted, sign up for a free ngrok account and get an auth token

### 3. Note the API URL

After running the notebook, you'll get a public URL for your API endpoint, which will look something like:
```
https://abcd-123-456-789-10.ngrok.io
```

### 4. Update Your Local Environment

1. Copy the `.env.example` file to `.env` in your local environment
2. Update the `OLLAMA_API_BASE` to point to your ngrok URL
3. Set `OLLAMA_REMOTE=true`

### 5. Run the Local Setup Script

```bash
python scripts/setup_llama4_scout.py
```

### 6. Test with CrewAI

```bash
python integration/crewai_example.py
```

## Important Notes

1. **Session Limits**: Google Colab sessions have a maximum runtime of 12 hours
2. **URL Changes**: The ngrok URL will change each time you restart the notebook
3. **Keep Running**: The notebook must remain running for the API to be accessible
4. **Cost Management**: Colab Pro is $9.99/month, much more affordable than dedicated GPU instances

## Troubleshooting

### No GPU Available

If you don't see an A100 GPU when running the first cell:
1. Make sure you have Colab Pro
2. Try disconnecting and reconnecting to the runtime
3. Try again at a different time (GPU availability varies)

### ngrok Connection Issues

If you have issues with ngrok:
1. Make sure you've signed up for a free ngrok account
2. Get a new auth token from the ngrok dashboard
3. Update the auth token in the notebook

### API Connection Issues

If your local code can't connect to the API:
1. Make sure the notebook is still running
2. Check that you're using the correct ngrok URL
3. Verify that the URL is accessible by testing in a browser
