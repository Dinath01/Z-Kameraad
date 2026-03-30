from fastapi import APIRouter
from pydantic import BaseModel
import time

from ml_model import predict_burnout

# Router for prediction endpoints
router = APIRouter()


# Request model for text input
class TextInput(BaseModel):
    text: str


@router.post("/predict")
def predict(input: TextInput):
    """
    Predict burnout level from input text.
    """
    start = time.time()

    result = predict_burnout(input.text)

    # Handle different return formats from the model
    if isinstance(result, dict):
        label_text = result.get("label")
        confidence = result.get("confidence", 0.9)
    else:
        label_text = result
        confidence = 0.9

    # Map label text to numeric level
    label_map = {
        "low": 1,
        "medium": 2,
        "high": 3
    }

    label = label_map.get(label_text, 0)

    end = time.time()

    return {
        "burnout_level": label,
        "burnout_meaning": label_text,
        "confidence": float(confidence),
        "response_time": end - start
    }