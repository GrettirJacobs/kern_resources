# Ollama on Render Deployment Guide

This guide provides step-by-step instructions for deploying Ollama with Llama 4 Scout Instruct on Render.com.

## Prerequisites

- A Render.com account
- A GitHub account with access to this repository
- A credit card for Render GPU instances (required even if using free credits)

## Deployment Steps

### 1. Fork or Clone the Repository

Ensure you have access to this repository on GitHub.

### 2. Log in to Render

Go to [render.com](https://render.com/) and log in to your account.

### 3. Create a New Blueprint

1. Click on "New" in the top right corner
2. Select "Blueprint" from the dropdown menu
3. Connect your GitHub account if you haven't already
4. Select the repository containing this code
5. Render will detect the `render.yaml` file and configure the service

### 4. Configure the Blueprint

1. Review the settings that Render has detected from the `render.yaml` file
2. Note that we're using the `gpu-a4000` plan, which costs approximately $1.20/hour
3. The service is configured to suspend after 15 minutes of inactivity to save costs
4. Click "Apply" to create the service

### 5. Wait for Deployment

1. Render will build and deploy the Ollama service
2. This may take several minutes as it needs to pull the Ollama Docker image and set up the environment

### 6. Pull the Llama 4 Scout Instruct Model

Once the service is deployed:

1. Go to the "Shell" tab in your Render dashboard for the Ollama service
2. Run the following command to pull the model:
   ```
   bash /opt/render/project/src/scripts/pull_model_on_render.sh
   ```
3. Wait for the model to download (this may take 10-15 minutes)

### 7. Test the Deployment

1. Once the model is pulled, you can test it with a simple query:
   ```
   curl -X POST https://ollama-llama4.onrender.com/api/generate -d '{
     "model": "llama4-scout-instruct",
     "prompt": "What is Kern Resources?",
     "stream": false
   }'
   ```
2. You should receive a JSON response with the generated text

### 8. Update Your Local Environment

1. Copy the `.env.example` file to `.env` in your local environment
2. Update the `OLLAMA_API_BASE` to point to your Render instance URL
3. Set `OLLAMA_REMOTE=true`

### 9. Run the Local Setup Script

```bash
python scripts/setup_llama4_scout.py
```

This will verify connectivity to your Render instance and save the model information.

## Managing Costs

The GPU instance (A4000) costs approximately $1.20/hour when running. To manage costs:

1. **Use Suspend on Idle**: The service is configured to suspend after 15 minutes of inactivity
2. **Manual Suspension**: You can manually suspend the service from the Render dashboard when not in use
3. **Monitor Usage**: Regularly check your Render dashboard for usage and billing information

## Troubleshooting

### Connection Issues

If you can't connect to your Ollama instance:

1. Check if the service is running in the Render dashboard
2. Verify that the service hasn't been suspended due to inactivity
3. Check the logs for any errors

### Model Loading Issues

If the model fails to load:

1. Check if there's enough disk space (50GB is allocated)
2. Try pulling the model again using the script
3. Check the logs for any specific error messages

### Performance Issues

If responses are slow:

1. The first request after suspension will be slow as the service needs to wake up
2. Check if the GPU is being fully utilized
3. Consider using a larger GPU instance if needed

## Next Steps

Once your Ollama instance is running on Render, you can:

1. Test the integration with CrewAI using the example script
2. Develop your own applications that use the Llama 4 Scout Instruct model
3. Consider fine-tuning the model for your specific use case
