from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize model and tokenizer as None (lazy loading)
model = None
tokenizer = None

def load_model():
    """Lazy load the model and tokenizer"""
    global model, tokenizer
    if model is None:
        model_id = os.getenv("MODEL_ID", "meta-llama/Llama-4-Scout-17B-E")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto"
        )

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route("/generate", methods=["POST"])
def generate_text():
    """Generate text based on the input prompt"""
    try:
        data = request.get_json()
        if not data or "prompt" not in data:
            return jsonify({"error": "No prompt provided"}), 400

        # Load model if not already loaded
        if model is None:
            load_model()

        # Get generation parameters
        prompt = data["prompt"]
        max_length = data.get("max_length", 100)
        temperature = data.get("temperature", 0.7)
        top_p = data.get("top_p", 0.9)

        # Generate text
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
            do_sample=True
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return jsonify({"generated_text": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
