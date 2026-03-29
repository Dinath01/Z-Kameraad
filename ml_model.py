from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch
import os

# Get absolute path to model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "burnout_roberta")

# Load model + tokenizer
tokenizer = RobertaTokenizer.from_pretrained(MODEL_PATH)
model = RobertaForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()

def predict_burnout(text: str):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    predicted_class_id = torch.argmax(logits, dim=1).item()

    # ⚠️ CHANGE THIS BASED ON YOUR TRAINING
    labels = ["low", "medium", "high"]

    return labels[predicted_class_id]