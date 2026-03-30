import os
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification

# Resolve absolute path to the trained model directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "burnout_roberta")

# Load tokenizer and model once at startup
tokenizer = RobertaTokenizer.from_pretrained(MODEL_PATH)
model = RobertaForSequenceClassification.from_pretrained(MODEL_PATH)

# Set model to evaluation mode
model.eval()


def predict_burnout(text: str):
    """
    Predict burnout level from input text using the trained RoBERTa model.
    """

    # Tokenize input text
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    # Run inference without gradient calculation
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # Get predicted class index
    predicted_class_id = torch.argmax(logits, dim=1).item()

    # Map prediction index to label (must match training order)
    labels = ["low", "medium", "high"]

    return labels[predicted_class_id]