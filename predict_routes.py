from fastapi import APIRouter
from pydantic import BaseModel
from ml_model import predict_burnout

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/predict")
def predict(input: TextInput):
    result = predict_burnout(input.text)
    return {
        "prediction": result
    }